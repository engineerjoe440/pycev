"""
pycev: A compressed event record reader for SEL CEV files.

Author(s):
  - Joe Stanley: joe_stanley@selinc.com  engineerjoe440@gmail.com

Homepage: https://github.com/engineerjoe440/pycev

SEL Protocol Application Guide: https://selinc.com/api/download/5026/
SEL Compressed ASCII (CASCII) Application Guide: https://selinc.com/api/download/5021/
"""

# Standard Imports
import os
import re
import time
import inspect
import warnings
from collections import namedtuple

# Local Imports

# Describe Package for External Interpretation
_name_ = "selcev"
_version_ = "0.0"
__version__ = _version_  # Alias the Version String


EVENT_SETTINGS_SEP = '"SETTINGS","02E1"'

RE_ROW_CONTENTS = re.compile(r'(.*,)"(.*?)"')


# Define Function to Evaluate Checksum
def _eval_checksum( data, constrain=False ):
    """
    *Evaluate the expected checksum for specific data row*

    This function accepts a string, and calculates the checksum
    of the bytes provided.

    Parameters
    ----------
    data:       [str, bytes]
                The bytestring which should be evaluated for the
                checksum.
    constrain:  bool, optional
                Control to specify whether the value should be
                constrained to an 8-bit representation, defaults
                to False.
    
    Returns
    -------
    checksum:   int
                The fully evaluated checksum.
    """
    # Evaluate the sum
    if isinstance(data, str):
        checksum = sum(map(ord, data))
    else:
        checksum = sum(data)
    # Cap the Value if Needed
    if constrain:
        checksum = checksum & 0xff # Bit-wise and with 8-bit maximum
    return checksum

# Define Function to Interpret Row-Wise Checksum for Validity
def row_wise_checksum(row_data):
    """
    *Identify the data and validate it with included checksum*

    Events should contain rows of data, where each row appears
    as:

    "some,data,in,the,event","checksum"

    Knowing this format, this function will separate the data
    from the checksum, and use the checksum to evaluate the
    validity of the data. The resulting data will be returned
    as a namedtuple as: Row('data':str, 'validity':bool)

    Parameters
    ----------
    row_data:   str
                The string containing all row data in form
                described above.
    
    Returns
    -------
    row:        namedtuple
                The namedtuple containing the separated data
                and validity marker in the form of:
                Row('data':str, 'validity':bool)
    """
    # Define the namedtuple Structure used for Return
    Row = namedtuple('Row', ['data', 'validity'])
    # Clean Input Data
    row_data = row_data.replace('\r','')
    row_data = row_data.replace('\n','')
    # Use RegEx to Extract Valuable Data
    context = re.findall(RE_ROW_CONTENTS, row_data)
    # Validate Context
    if len(context) == 1:
        context = context[0] # Unwrap
        if len(context) == 2:
            # Successfully Extracted Data
            row_contents, checksum_str = context # Extract
            # Evaluate Checksum as INT
            checksum_int = int.from_bytes(  bytes.fromhex(checksum_str),
                                            byteorder='big',
                                            signed=True )
            # Calculate Checksum
            checksum = _eval_checksum(data=row_contents)
            # Remove Trailing Comma if Present
            if row_contents.endswith(','):
                row_contents = row_contents[:-1] # Trim Comma
            # Pack Structure
            row = Row(data=row_contents, validity=(checksum==checksum_int))
            return row
        else:
            raise ValueError("Failed to unwrap context from event data row.")
    else:
        print(row_data, context)
        raise ValueError("Failed to locate appropriate data contents.")

# Define Function to Split Event Data from Relay Settings
def split_event_and_relay_data(data):
    """
    *Split the Event Data from Relay Settings*

    This function accepts the full text from a CEV file, and separates
    the event-record data from the relay's configuration settings.
    These two separated items are returned as a named-tuple which is
    formed as: EventData('record':str, 'settings':str)

    Parameters
    ----------
    data:       str
                The string containing all data read from the CEV file.
    
    Returns
    -------
    event:      namedtuple
                The namedtuple containing the 'record' and 'settings'
                information, each being the so-described elements from
                the event record which have been read. namedtuple is
                of the form: EventData('record':str, 'settings':str)
                where 'record' is the event information, and 'settings'
                is the relay's configuration settings.
    """
    # Define the namedtuple Structure used for Return
    EventData = namedtuple('EventData', ['record', 'settings'])
    # Gather the Components from the Event Record
    record, settings = data.split(EVENT_SETTINGS_SEP)
    # Prepare Structure
    event = EventData(record=record, settings=settings)
    return event


# Define the Primary Class
class Cev():
    """
    
    """
    
    def __init__(self, file=None, data=None, **kwargs):
        """
        Class initialization with optional data input methods for file-path
        and raw data as either a string or bytes.
        """
        # Handle Encoding Type if Provided
        if "encoding" in kwargs:
            encoding = kwargs['encoding']
        else:
            encoding = None

        # Handle Decoding Option if Provided
        if "decode_opt" in kwargs:
            self._decode_opt = kwargs['decode_opt']
        elif "decode_option" in kwargs:
            self._decode_opt = kwargs['decode_option']
        else:
            self._decode_opt = 'strict'
        
        # Handle Warnings Override
        if "ignore_warnings" in kwargs:
            self.ignore_warnings = kwargs["ignore_warnings"]
        else:
            self.ignore_warnings = False
        
        # Prepare Defaults
        self.data = ''
        self.record = ''
        self.settings = ''
        self.record_lines = []

        # Prepare Data or File if Provided
        if file is not None:
            if not os.path.exists( file ):
                raise ValueError("Argument `file` must be a valid file-path to a CEV file.")
            else:
                self.load( file=file, encoding=encoding )
        elif data is not None:
            self.load_data( data=data, encoding=encoding )
        

    # Define Simple File Extension Validator
    def _validate_extension(self, file):
        """ Validate Extension is of *.CEV Format """
        filename, ext = os.path.splitext(file)
        if 'CEV' not in ext.upper():
            # Throw Warning to User
            if not self.ignore_warnings:
                # Capture Pertinent Information
                parent = inspect.stack()[2]
                callfile = parent.filename
                lineno   = parent.lineno
                function = parent.function
                warnings.showwarning(
                    message=f'File does not appear to use "CEV" extension, instead is "{ext}".',
                    category=UserWarning,
                    filename=callfile,
                    lineno=lineno,
                )
        # Proceed Without Exception
    
    # Define Simple Decoder for Data
    def _decode(self, data, encoding):
        """ Simply Decode the Data Using the Specified Encoding Format """
        if encoding != None:
            return data.decode(encoding, self._decode_opt)
        else:
            return data
    
    # Define Function to Prepare Record and Validate Checksums
    def _prepare_and_validate_record(self):
        """ Simply Split the Record and Settings, then Evaluate Checksums """
        # Split Data
        self.record, self.settings = split_event_and_relay_data(self.data)
        valid = True # Assume Good
        # Evaluate Record Checksums
        for line in self.record.split('\n'):
            if line == '' or line == None or line == ' ':
                continue
            # Collect Line Data and
            content, validity = row_wise_checksum(line)
            self.record_lines.append(content)
            valid = valid and validity
        # Throw Warning to User
        if (not valid) and (not self.ignore_warnings):
            # Capture Pertinent Information
            parent = inspect.stack()[2]
            callfile = parent.filename
            lineno   = parent.lineno
            function = parent.function
            warnings.showwarning(
                message='Record data appears to be malformed, and fails checksum validation.',
                category=UserWarning,
                filename=callfile,
                lineno=lineno,
            )
        # Return the Validity Signal
        return valid
    
    # Define File Loader Method
    def load(self, file, encoding=None):
        """
        
        """
        if not os.path.exists( file ):
            raise ValueError("Argument `file` must be a valid file-path to a CEV file.")
        # Validate file Extension
        self._validate_extension(file)
        # Read File with Encoding
        with open(file, 'r', encoding=encoding) as fObj:
            self.data = fObj.read() # Gather ALL Data From File
        # Prepare Record Information
        self._prepare_and_validate_record()
    
    # Define Data Loader Method
    def load_data(self, data, encoding=None):
        """
        
        """
        # Decode Data As Needed
        self.data = self._decode(data, encoding=encoding)
        # Prepare Record Information
        self._prepare_and_validate_record()



# Alias the Class: `Cev` to `CEV` for Convenience
CEV = Cev

# Define Simple Builtin Test
if __name__ == '__main__':
    print(row_wise_checksum('"SETTINGS","02E1"'))
    filepath = input("Specify a CEV file to test against: ")
    x = Cev(file=filepath)


# END