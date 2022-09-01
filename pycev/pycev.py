################################################################################
"""
pycev: A compressed event record reader for SEL CEV files.

Author(s):
  - Joe Stanley: joe_stanley@selinc.com  engineerjoe440@gmail.com

Homepage: https://github.com/engineerjoe440/pycev

SEL Protocol Application Guide:
    https://selinc.com/api/download/5026/

SEL Compressed ASCII (CASCII) Application Guide:
    https://selinc.com/api/download/5021/

───────────────────────────────────────────────────────────────────────────────

MIT License

Copyright (c) 2020 Joe Stanley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
################################################################################

# Standard Imports
import os
import re
import inspect
from typing import Union
import warnings
import datetime as dt
from collections import namedtuple

# Describe Package for External Interpretation
_name_ = "pycev"
_version_ = "0.1.0"
__version__ = _version_  # Alias the Version String


# Define Global Strings
EVENT_SETTINGS_SEP = '"SETTINGS","02E1"'
ANALOG_SAMPLES = "SAM/CYC_A"
DIGITAL_SAMPLES = "SAM/CYC_D"
TRIGGER_KEY_CHAR = ">"
FREQUENCY_KEY = "FREQ"


# Custom Exceptions and Warnings
class MalformedChecksumFailure(UserWarning):
    """Record data appears to be malformed, and fails checksum validation."""

class UnexpectedFileExtension(UserWarning):
    """File does not appear to use expected "CEV" extension."""

class MalformedHeadingDataMismatch(Exception):
    """CEV is Malformed - Heading and Data Section Lengths do not Match."""

class MalformedNoFIDFound(Exception):
    """CEV is Malformed - FID String Could not be Located."""

class MalformedNoSampleNumberFound(Exception):
    """CEV is Malformed - Number of Samples Could not be Located."""


# Define Function to Interpret Row-Wise Checksum for Validity
def row_wise_checksum(row_data, constrain=True):
    """
    Identify the data and validate it with included checksum.

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
    row_data = row_data.replace('\r', '')
    row_data = row_data.replace('\n', '')
    # Successfully Extracted Data
    row_contents = row_data[:-6]  # Remove Checksum Characters
    checksum_str = row_data[-6:].replace('"', '')  # Keep Checksum Only
    # Evaluate Checksum as INT
    checksum_int = int.from_bytes(
        bytes.fromhex(checksum_str),
        byteorder='big',
        signed=False
    )
    # Evaluate the Checksum
    if isinstance(row_contents, str):
        checksum = sum(map(ord, row_contents))
    else:
        checksum = sum(row_contents)
    # Cap the Value if Needed
    if constrain:
        checksum = checksum & 0xffff  # Bit-wise AND with 16-bit maximum
    # Remove Trailing Comma if Present
    if row_contents.endswith(','):
        row_contents = row_contents[:-1]  # Trim Comma
    # Pack Structure
    valid = checksum == checksum_int
    row = Row(data=row_contents, validity=valid)
    return row


# Define Function to Split Event Data from Relay Settings
def split_event_and_relay_data(data):
    """
    Split the Event Data from Relay Settings.

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
    SEL CEV File Reader.

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

    Examples
    --------
    >>> from pycev import CEV
    >>> # Load a file and parse, directly.
    >>> record = CEV(file="./event-report.cev")
    >>> print("Trigger time = {}s".format(record.trigger_time))
    """

    def __init__(self, file: str = None, data: Union[str, bytes] = None,
                 **kwargs):
        """
        Prepare CEV Reader.

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
        self.time = []
        self.trigger_time = dt.datetime(1970, 1, 1)  # Default to Epoch
        self.channels_count = 0
        self.analog_channels = []
        self.analog_channel_ids = []
        self.status_channels = []
        self.status_channel_ids = []
        self.digital_channels = self.status_channels  # Alias the Digitals
        self.digital_channel_ids = self.status_channel_ids  # Alias Digitals
        self.analog_count = 0
        self.status_count = 0
        self.digital_count = 0
        self.frequency = 0.0

        self.year = 1970
        self.month = 1
        self.day = 1
        self.hour = 0
        self.min = 0
        self.sec = 0
        self.msec = 0

        self._ignored_channels = []
        self._trig_column = -1
        self._trig_row = 0
        self._analog_samp_timedelta = None
        self._digital_samp_timedelta = None
        self._properties = {}  # Empty Dictionary of the Keys

        # Prepare Data or File if Provided
        if isinstance(file, (str, bytes)):
            self.load(file=file, encoding=encoding)
        elif hasattr(file, "read"): # Probably a file-like object?
            self.load_data(data=file.read(), encoding=encoding)
        elif isinstance(data, (str, bytes)):
            self.load_data(data=data, encoding=encoding)

    # Define Simple Method to Identify Class Keys
    def _keys(self):
        """Capture Class Attributes as Keys."""
        return self.__dict__.keys()

    # Define Simple File Extension Validator
    def _validate_extension(self, file):
        """Validate Extension is of *.CEV Format."""
        if not os.path.exists(file):
            raise FileNotFoundError(
                "Argument `file` must be a valid file-path to a CEV file."
            )
        _, ext = os.path.splitext(file)
        if 'CEV' not in ext.upper():
            # Throw Warning to User
            if not self.ignore_warnings:
                # Capture Pertinent Information
                parent = inspect.stack()[2]
                callfile = parent.filename
                lineno = parent.lineno
                warnings.showwarning(
                    message=(
                        'File does not appear to use "CEV" extension,' +
                        f' instead is "{ext}".'
                    ),
                    category=UnexpectedFileExtension,
                    filename=callfile,
                    lineno=lineno,
                )
        # Proceed Without Exception

    # Define Simple Decoder for Data
    def _decode(self, data, encoding):
        """Simply Decode the Data Using the Specified Encoding Format."""
        if encoding is not None:
            return data.decode(encoding, self._decode_opt)
        else:
            return data

    # Define Function to Prepare Record and Validate Checksums
    def _prepare_and_validate_record(self):
        """Simply Split the Record and Settings, then Evaluate Checksums."""
        # Split Data
        self.record, self.settings = split_event_and_relay_data(self.data)
        invalid_lines = {}
        # Evaluate Record Checksums
        for i, line in enumerate(self.record.split('\n')):
            if line == '' or (line is None) or line == ' ':
                continue
            # Collect Line Data and
            content, validity = row_wise_checksum(line)
            self.record_lines.append(content)
            if not validity:
                invalid_lines[i + 1] = content
        # Throw Warning to User
        if invalid_lines and (not self.ignore_warnings):
            # Capture Pertinent Information
            parent = inspect.stack()[2]
            callfile = parent.filename
            lineno = parent.lineno
            warnings.showwarning(
                message=(
                    'Record data appears to be malformed, '
                    'and fails checksum validation for lines: '
                    ", ".join([str(ind) for ind in invalid_lines])
                ),
                category=MalformedChecksumFailure,
                filename=callfile,
                lineno=lineno,
            )
        # Return the Validity Signal
        return len(invalid_lines) == 0

    # Define Internal Test to Identify Header
    def _is_header(self, row_data):
        """Test Function to Evaluate Whether Row is Header."""
        if row_data.startswith('"') and row_data.endswith('"'):
            return True
        else:
            return False

    # Define Internal Test to Identify Data Row
    def _is_data(self, row_data):
        """Test Function to Evaluate Whether Row isn't Header."""
        return not self._is_header(row_data=row_data)

    # Define Primary Parsing Function
    def _parse_record(self):
        """Primary Parsing Function to Interpret the CEV."""
        # Operate on "Row-Pairs" with two Rows at Once to Pair Key with Value
        # Start with Row-Index-Zero (first row), and Assuming Header
        iRow = 0
        # Only Validate the First Row, Since Second Row Should Contain FID
        header = self._is_header(self.record_lines[iRow])

        # Manage the Initial Record Data
        while header:
            # Clean and Split the Heading and Content
            heading_row = self.record_lines[iRow].replace('"', '').split(',')
            content_row = self.record_lines[iRow + 1]
            content_row = content_row.replace('"', '').split(',')
            if not len(heading_row) == len(content_row):
                print(heading_row)
                print(content_row)
                raise MalformedHeadingDataMismatch(
                    "CEV may be malformed, heading and data length don't match"
                )
            # Load the Data into Class Keys
            for key, value in zip(heading_row, content_row):
                # Verify Attribute and Load
                key_lower = key.lower()
                if key_lower in self._keys():
                    if callable(self.__dict__[key_lower]):
                        continue  # Don't Overwrite a Callable!
                if (key.find('/') == -1) and (key.find('(') == -1):
                    # Valid Class Variable Name, Load Directly
                    self.__dict__[key_lower] = value
                # Store the Data as a Property
                self._properties[key] = value

            # Check Next Group
            header = (
                self._is_header(self.record_lines[iRow + 2]) and
                self._is_data(self.record_lines[iRow + 3]) and
                self._is_header(self.record_lines[iRow + 4])
            )
            # Increment Row Index
            iRow += 2

        # Following the Primary Header Content, a Single Header Remains
        # with the Analog and Digital Channel Names.
        # Split on either a comma (',') or a space (' ')
        channels = re.split(r',| ', self.record_lines[iRow])
        is_analog = True  # First Channel from Left is Analog

        # Identify Channel Names as Analog or Digital
        for i, channel in enumerate(channels):
            # Check if Trig Channel
            if '"TRIG"' == channel:
                is_analog = False
                self._ignored_channels.append(i)
                self._trig_column = i
                continue  # Don't Track the TRIP Channel
            elif '*' == channel:
                self._ignored_channels.append(i)
                continue  # Don't Track Unused Channels
            elif '' == channel:
                continue  # Don't Track Empty Channel Names
            # Remove Double Quotes
            channel = channel.replace('"', '')
            # Channel Must be Valid, Append Name to Either Analog or Digital
            if is_analog:
                self.analog_channel_ids.append(channel)
            else:
                self.status_channel_ids.append(channel)

        iRow += 1  # Increment Past the Data Heading Column

        # Characterize Number of Channels
        self.analog_count = len(self.analog_channel_ids)
        self.status_count = len(self.status_channel_ids)

        # Build the Channel Lists According to Sizes
        self.analog_channels = [[] for x in range(self.analog_count)]
        self.status_channels = [[] for x in range(self.status_count)]

        # Iterate over Data Rows to Load Channels
        numRows = len(self.record_lines)
        initRow = iRow
        while iRow < numRows:
            channels = self.record_lines[iRow].split(',')
            # Track Analog Quantities
            k = 0
            for i in range(0, self.analog_count):
                value = float(channels[i])
                # Verify that Channel Index Shouldn't be Ignored
                if i not in self._ignored_channels:
                    self.analog_channels[i].append(value)
                k = i + 2

            # Identify Trigger Data Row
            if TRIGGER_KEY_CHAR in channels[k-1]:
                self._trig_row = iRow - initRow

            # Format the Digitals
            digital_string = channels[k].replace('"', '')
            digitals = []
            # Iteratively Process the Hex String
            while len(digital_string) > 0:
                hex_byte = digital_string[:2]
                digital_string = digital_string[2:]
                # Identify the Bits
                binary_byte = bin(int(hex_byte, base=16))
                # Use zfill to pad the string with zeros as we want
                # all 8 digits of the byte.
                bits_string = binary_byte[2:].zfill(8)
                digitals.extend([int(bit) for bit in bits_string])

            # Track Digital Quantities
            for i in range(0, self.status_count):
                # Verify that Channel Index (Offset by the TRIG channel)
                # Shouldn't be Ignored
                if (i + self._trig_column) not in self._ignored_channels:
                    self.status_channels[i].append(digitals[i])

            iRow += 1  # Increment Row Index

    # Define Event Trigger Time Evaluator
    def _eval_trigger_time(self):
        """Use Time Information to Identify Trigger Time."""
        usec = int(self.msec) * 1000
        self.trigger_time = dt.datetime(
            year=int(self.year),
            month=int(self.month),
            day=int(self.day),
            hour=int(self.hour),
            minute=int(self.min),
            second=int(self.sec),
            microsecond=usec
        )

    # Define Frequency Identifier
    def _eval_frequency(self):
        """Identify and load the system nominal frequency."""
        self.frequency = float(self._properties.get(FREQUENCY_KEY, 60.0))

    # Define FID Cleaner
    def _clean_fid(self):
        """Store the 'raw' FID in a New Variable, and Clean Existing FID."""
        try:
            self.raw_fid = self.fid
            self.fid = self.fid.split('=')[1]
        except Exception as err:
            raise MalformedNoFIDFound(
                "Failed to load relay FID from CEV"
            ) from err

    # Define Samples-Per-Cycle Evaluator
    def _eval_samples_per_cycle(self):
        """Identify the Samples/Cycle Indicators, Calculate the Deltas."""
        try:
            # Extract the Number of Samples per Cycle, Evaluate Milliseconds
            ms_per_cyc = 1000 / self.frequency
            analog_ms = ms_per_cyc / float(self._properties[ANALOG_SAMPLES])
            digital_ms = ms_per_cyc / float(self._properties[DIGITAL_SAMPLES])
        except KeyError as err:
            raise MalformedNoSampleNumberFound(
                "Failed to identify number of samples per cycle"
            ) from err
        # Prepare the TimeDeltas
        self._analog_samp_timedelta = dt.timedelta(milliseconds=analog_ms)
        self._digital_samp_timedelta = dt.timedelta(milliseconds=digital_ms)

    # Define Timestamp Loader
    def _eval_timestamps(self):
        """Evaluate event timestamps."""
        # Calculate the first timestamp
        initTimeDelta = self._analog_samp_timedelta * self._trig_row
        self.time = [self.trigger_time - initTimeDelta]
        # Iteratively Calculate Remaining Timestamps
        for _ in range(1, len(self.analog_channels[0])):
            # Add Timedelta to Most Recent Time Value
            self.time.append(self.time[-1] + self._analog_samp_timedelta)

    # Define File Loader Method
    def load(self, file: str, encoding: str = None):
        """
        *CEV File Loader Method*.

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
        FileNotFoundError
            If the file cannot be located on the system
        MalformedHeadingDataMismatch
            If the file contains a header and content row pair which do not
            share an equal number of columns.

        Warns
        -----
        UnexpectedFileExtension
            If the uppercase-cast file extension is not ".CEV"
        MalformedChecksumFailure
            If any of the CEV line-wise checksums do not evaluate successfully

        Examples
        --------
        >>> from pycev import CEV
        >>> # Load a file and parse, directly.
        >>> record = CEV() # Create the parser instance
        >>> record.load(file="./event-report.cev")
        >>> print("Trigger time = {}s".format(record.trigger_time))
        """
        # Switch between Handling File-Path, or File-Like-Object
        if isinstance(file, str):
            # Validate file Extension
            self._validate_extension(file)
            # Read File with Encoding
            with open(file, 'r', encoding=encoding) as file_obj:
                self.data = file_obj.read()  # Gather ALL Data From File
        elif hasattr(file, "read"):
            self.data = file.read()
        # Process the Data and Load Record
        self.load_data(data=None)

    # Define Data Loader Method
    def load_data(self, data: Union[str, bytes], encoding: str = None):
        """
        *CEV Data Loader Method*.

        Use this method to load the data from a CEV file which has already been
        read, or data which is being streamed to the class (i.e., an active
        connection to a relay). This method will parse the data and load the
        class attributes and structures appropriately.

        Parameters
        ----------
        data:       [str, bytes]
                    String of the full file content.
        encoding:   str, optional
                    String specifying the encoding format (if required) in
                    which the file is stored. This may be used for files of
                    format 'utf-8', for example.

        See Also
        --------
        load            : Load data from a CEV file.

        Raises
        ------
        MalformedHeadingDataMismatch
            If the file contains a header and content row pair which do not
            share an equal number of columns.

        Warns
        -----
        MalformedChecksumFailure
            If any of the CEV line-wise checksums do not evaluate successfully

        Examples
        --------
        >>> from pycev import CEV
        >>> # Load a file and parse, directly.
        >>> record = CEV() # Create the parser instance
        >>> with open("./event-report.cev", 'r') as file:
        ...     data = file.read()
        >>> record.load_data(data=data)
        >>> print("Trigger time = {}s".format(record.trigger_time))
        """
        # Method is Called Internally with `data=None`
        # Don't Try Loading in this Case
        if data is not None:
            # Decode Data As Needed
            self.data = self._decode(data, encoding=encoding)
        # Prepare Record Information
        self._prepare_and_validate_record()
        # Parse the Record
        self._parse_record()
        # Determine the Trigger Time
        self._eval_trigger_time()
        # Identify Nominal System Frequency
        self._eval_frequency()
        # Clean FID
        self._clean_fid()
        # Rationalize Number of Samples per Cycle
        self._eval_samples_per_cycle()
        # Evaluate the Timestamps
        self._eval_timestamps()

    # Define Method to Access the Analog Channel by Name
    def get_analog(self, channel_name: str):
        """
        *Extract an analog channel by name*.

        Use this method to return the list of analog values
        associated with the particular analog channel with
        the specified name.

        Parameters
        ----------
        channel_name:   str
                        Name of the analog channel which
                        should be extracted.

        Returns
        -------
        channel:    list of float
                    The analog channel values in a zero-based
                    list.

        See Also
        --------
        get_status  : Collect the digital channel status for a
                      specified name.
        get_digital : Collect the digital channel status for a
                      specified name.

        Examples
        --------
        >>> from pycev import CEV
        >>> # Load a file and parse, directly.
        >>> record = CEV() # Create the parser instance
        >>> record.load(file="./event-report.cev")
        >>> record.get_analog("FREQ")
        [...]
        """
        # Identify the Analog Channel Index
        channel_index = self.analog_channel_ids.index(channel_name)
        # Return the Analog Channel
        return self.analog_channels[channel_index]

    # Define Method to Access the Digital Channel by Name
    def get_status(self, channel_name: str):
        """
        *Extract an digital channel by name*.

        Use this method to return the list of digital values
        associated with the particular digital channel with
        the specified name.

        Parameters
        ----------
        channel_name:   str
                        Name of the digital channel which
                        should be extracted.

        Returns
        -------
        channel:    list of bool
                    The digital channel values in a zero-based
                    list.

        See Also
        --------
        get_analog  : Collect the analog channel status for a
                      specified name.
        get_status  : Collect the digital channel status for a
                      specified name.
        get_digital : Collect the digital channel status for a
                      specified name.

        Examples
        --------
        >>> from pycev import CEV
        >>> # Load a file and parse, directly.
        >>> record = CEV() # Create the parser instance
        >>> record.load(file="./event-report.cev")
        >>> record.get_status("TRIPLED")
        [...]
        >>> record.get_digital("TRIPLED")
        [...]
        """
        # Identify the Digital Channel Index
        channel_index = self.status_channel_ids.index(channel_name)
        # Return the Digital Channel
        return self.status_channels[channel_index]

    # Alias `get_status` to `get_digital`
    get_digital = get_status


# Alias the Class: `Cev` to `CEV` for Convenience
CEV = Cev


# END
