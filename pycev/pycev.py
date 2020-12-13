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
import datetime as dt
from collections import namedtuple

# Local Imports

# Describe Package for External Interpretation
_name_ = "pycev"
_version_ = "0.0"
__version__ = _version_  # Alias the Version String


EVENT_SETTINGS_SEP = '"SETTINGS","02E1"'


# Define Function to Evaluate Checksum
def _eval_checksum( data, constrain=True ):
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
        checksum = checksum & 0xffff # Bit-wise AND with 16-bit maximum
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
    # Successfully Extracted Data
    row_contents = row_data[:-6] # Remove Checksum Characters
    checksum_str = row_data[-6:].replace('"','') # Keep Checksum Only
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
    *SEL CEV File Reader*
    
    This class serves to provide functionality to read SEL (Schweitzer
    Engineering Laboratories) Compressed EVent records (CEV files) and
    grant pragmatic access to the key components of these records. The
    methods, attributes, and properties of this class serve to expose
    data in a manner that supports scientific analysis and allow common
    data-science tools such as NumPy, Matplotlib, Pandas, and others to
    conveniently interpret information. This all is in an effort to
    support data scientists and engineers to make empowered, intelligent
    decisions about the power systems which they are responsible for.
    
    Within this module, this class (`Cev`) is also aliased as CEV for
    programming convenience, and to allow users to access the functionality
    in a format that is consistent with their work.
    
    Parameters
    ----------
    file:       str, optional
                String describing the relative or fully qualified path to
                the CEV file that should be read. Optionally used during
                class initialization, may also be loaded using the `load`
                method.
    data:       str, optional
                String describing all contents of the CEV file as read.
                Optionally used during class initialization to pre-load
                the contents of the CEV file.
    **kwargs:   dict, optional
                Additional optional parameters which may be specified
                during class initialization. Common arguments include:
                
                    - encoding:     str, file encoding such as 'utf-8'
                    - decode_opt:   str, file decoding option such as
                                    'strict', 'ignore', 'replace', or
                                    'backslashreplace' as defined by
                                    standard str.decode method.
                    - ignore_warnings: bool, control to ignore warnings
                
                Class initialization may include one or more kwargs,
                but none are required.
    
    Attributes
    ----------
    analog_channels:        list of list of float
                            List of lists containing the analog samples
                            for each channel.
    analog_channel_ids:     list of str
                            List of the analog channel names whose index
                            values correspond directly to the channel
                            datasets in `analog_channels`.
    analog_count:           int
                            Number of analog channels present in CEV.
    channels_count:         int
                            Total number of analog and digital (status)
                            channels in CEV.
    data:                   str
                            Full string context of the entire CEV record;
                            includes both the event information and relay
                            settings that were included with the record.
    digital_channels:       list of list of bool
                            List of lists containing boolean states for
                            each digital (status) channel present in CEV.
                            This list presents itself as an alias to the
                            `status_channels` class attribute.
    digital_channel_ids:    list of str
                            List of the digital (status) channel names
                            whose index values correspond directly to the
                            channel datasets in `digital_channels`. This
                            list presents itself as an alias to the
                            `status_channel_ids` class attribute.
    digital_count:          int
                            Number of digital channels present in the CEV.
    fid:                    str
                            Relay firmware identification string; does not
                            include the 'FID=' specifier.
    frequency:              float
                            The recorded nominal frequency present in the
                            CEV.
    raw_fid:                str
                            "Raw" relay firmware identification string;
                            includes the 'FID=' specifier to lead the string.
    record:                 str
                            Event record data-sub-section contents; contains
                            only the event-related data and heading fields of
                            the CEV that was loaded.
    record_lines:           list of str
                            Row-wise split contents of the record with all
                            newline and carriage-return characters removed.
    settings:               str
                            Relay settings data-sub-section contents; contains
                            only the relay settings portion of the CEV that
                            was loaded.
    status_channels:        list of list of bool
                            List of lists containing boolean states for
                            each status (digital) channel present in CEV.
                            This list is aliased to the `digital_channels`
                            class attribute.
    status_channel_ids:     list of str
                            List of the status (digital) channel names
                            whose index values correspond directly to the
                            channel datasets in `status_channels`. This
                            list is aliased to the `digital_channel_ids`
                            class attribute.
    status_count:           int
                            Number of status channels present in the CEV.
    trigger_time:           datetime
                            Date-time structure indicating when the event
                            was "triggered" by protection logic in the relay.
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
        self.fid = ''
        self.raw_fid = ''
        self.trigger_time = dt.datetime(1970, 1, 1) # Default to Epoch
        self.channels_count = 0
        self.analog_channels = []
        self.analog_channel_ids = []
        self.status_channels = []
        self.status_channel_ids = []
        self.digital_channels = self.status_channels # Alias the Digitals
        self.digital_channel_ids = self.status_channel_ids # Alias the Digital Names
        self.analog_count = 0
        self.status_count = 0
        self.digital_count = 0 
        self.frequency = 0.0

        self._ignored_channels = []
        self._trig_column = -1

        # Prepare Data or File if Provided
        if file is not None:
            self.load( file=file, encoding=encoding )
        elif data is not None:
            self.load_data( data=data, encoding=encoding )
    
    # Define Simple Method to Identify Class Keys
    def _keys(self):
        """ Capture Class Attributes as Keys """
        return self.__dict__.keys()

    # Define Simple File Extension Validator
    def _validate_extension(self, file):
        """ Validate Extension is of *.CEV Format """
        if not os.path.exists( file ):
            raise ValueError("Argument `file` must be a valid file-path to a CEV file.")
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
    
    # Define Internal Test to Identify Header
    def _is_header(self, row_data):
        """ Simple Test Function to Evaluate Whether Row is Header """
        if row_data.startswith('"') and row_data.endswith('"'):
            return True
        else:
            return False
    
    # Define Internal Test to Identify Data Row
    def _is_data(self, row_data):
        """ Simple Test Function to Evaluate Whether Row isn't Header """
        return not self._is_header(row_data=row_data)
    
    # Define Primary Parsing Function
    def _parse_record(self):
        """ Primary Parsing Function to Interpret the CEV """
        # Operate on "Row-Pairs" with two Rows at Once to Pair Key with Value
        # Start with Row-Index-Zero (first row), and Assuming Header
        iRow = 0
        # Only Validate the First Row, Since Second Row Should Contain FID
        header = self._is_header(self.record_lines[iRow])

        # Manage the Initial Record Data
        while header:
            # Clean and Split the Heading and Content
            heading_row = self.record_lines[ iRow ].replace('"','').split(',')
            content_row = self.record_lines[ iRow + 1 ].replace('"','').split(',')
            if not len(heading_row) == len(content_row):
                print(heading_row)
                print(content_row)
                raise ValueError("CEV may be malformed, heading and data did not match in length.")
            # Load the Data into Class Keys
            for key, value in zip(heading_row, content_row):
                # Verify Attribute and Load
                key = key.lower()
                if key in self._keys():
                    if callable( self.__dict__[key] ):
                        continue # Don't Overwrite a Callable!
                # Store the Data
                self.__dict__[key] = value
            
            # Check Next Group
            header = (
                self._is_header( self.record_lines[ iRow + 2 ] ) and
                self._is_data( self.record_lines[ iRow + 3 ] ) and
                self._is_header( self.record_lines[ iRow + 4 ] )
            )
            # Increment Row Index
            iRow += 2
        
        # Following the Primary Header Content, a Single Header Remains
        # with the Analog and Digital Channel Names.
        # Split on either a comma (',') or a space (' ')
        channels = re.split(r',| ', self.record_lines[ iRow ])
        is_analog = True # First Channel from Left is Analog

        # Identify Channel Names as Analog or Digital
        for i, channel in enumerate(channels):
            # Check if Trig Channel
            if '"TRIG"' == channel:
                is_analog = False
                self._ignored_channels.append(i)
                self._trig_column = i
                continue # Don't Track the TRIP Channel
            # Remove Double Quotes
            channel = channel.replace('"','')
            # Check if Unused Channel
            if ('*' == channel) or ('' == channel):
                self._ignored_channels.append(i)
                continue
            # Channel Must be Valid, Append Name to Either Analog or Digital
            if is_analog:
                self.analog_channel_ids.append(channel)
            else:
                self.status_channel_ids.append(channel)
        
        iRow += 1 # Increment Past the Data Heading Column

        # Characterize Number of Channels
        self.analog_count = len(self.analog_channel_ids)
        self.status_count = len(self.status_channel_ids)

        # Build the Channel Lists According to Sizes
        self.analog_channels = [ [] for x in range(self.analog_count) ]
        self.status_channels = [ [] for x in range(self.status_count) ]

        # Iterate over Data Rows to Load Channels
        numRows = len(self.record_lines)
        while iRow < numRows:
            channels = self.record_lines[ iRow ].split(',')
            # Track Analog Quantities
            for i in range(0, self.analog_count):
                self.analog_channels[i].append( channels[i] )
            
            iRow += 1 # Increment Row Index
                
    
    # Define Event Trigger Time Evaluator
    def _eval_trigger_time(self):
        """ Simple Function to Use Loaded Time Information to Identify Trigger Time """
        usec = int(self.msec) * 1000
        self.trigger_time = dt.datetime(
            year    = int(self.year),
            month   = int(self.month),
            day     = int(self.day),
            hour    = int(self.hour),
            minute  = int(self.min),
            second  = int(self.sec),
            microsecond = usec
        )
    
    # Define FID Cleaner
    def _clean_fid(self):
        """ Simply Store the 'raw' FID in a New Variable, and Clean Existing FID """
        self.raw_fid = self.fid
        self.fid = self.fid.split('=')[1]

    # Define File Loader Method
    def load(self, file, encoding=None):
        """
        *CEV File Loader Method*
        
        Use this method to load a CEV file, and parse its contents into the
        valuable class attributes and structure.
    
        Parameters
        ----------
        file:       str
                    String describing the relative or fully qualified path to
                    the CEV file that should be read. Optionally used during
                    class initialization, may also be loaded using the `load`
                    method.
        encoding:   str, optional
                    String specifying the encoding format (if required) in
                    which the file is stored. This may be used for files of
                    format 'utf-8', for example.
        
        See Also
        --------
        load_data       : Load data which has already been read from a file,
                          or is presented as a stream.
        
        Raises
        ------
        ValueError
            If the file cannot be located on the system
            If the file contains a header and content row pair which do not
                share an equal number of columns.
        
        Warns
        -----
        UserWarning
            If the uppercase-cast file extension is not ".CEV"
            If any of the CEV line-wise checksums do not evaluate successfully
        """
        # Validate file Extension
        self._validate_extension(file)
        # Read File with Encoding
        with open(file, 'r', encoding=encoding) as fObj:
            self.data = fObj.read() # Gather ALL Data From File
        # Process the Data and Load Record
        self.load_data(data=None)
    
    # Define Data Loader Method
    def load_data(self, data, encoding=None):
        """
        *CEV Data Loader Method*
        
        Use this method to load the data from a CEV file which has already been
        read, or data which is being streamed to the class (i.e., an active
        connection to a relay). This method will parse the data and load the
        class attributes and structures appropriately.
    
        Parameters
        ----------
        file:       str
                    String describing the relative or fully qualified path to
                    the CEV file that should be read. Optionally used during
                    class initialization, may also be loaded using the `load`
                    method.
        encoding:   str, optional
                    String specifying the encoding format (if required) in
                    which the file is stored. This may be used for files of
                    format 'utf-8', for example.
        
        See Also
        --------
        load            : Load data from a CEV file.
        
        Warns
        -----
        UserWarning
            If any of the CEV line-wise checksums do not evaluate successfully
        """
        # Method is Called Internally with `data=None`, Don't Try Loading in this Case
        if data != None:
            # Decode Data As Needed
            self.data = self._decode(data, encoding=encoding)
        # Prepare Record Information
        self._prepare_and_validate_record()
        # Parse the Record
        self._parse_record()
        # Determine the Trigger Time
        self._eval_trigger_time()
        # Clean FID
        self._clean_fid()



# Alias the Class: `Cev` to `CEV` for Convenience
CEV = Cev

# Define Simple Builtin Test
if __name__ == '__main__':
    print(row_wise_checksum('"SETTINGS","02E1"'))
    filepath = input("Specify a CEV file to test against: ")
    x = Cev(file=filepath)
    print(x.fid)
    print(x.trigger_time)
    print(x.analog_channel_ids)
    print(x.analog_channels[-1])


# END