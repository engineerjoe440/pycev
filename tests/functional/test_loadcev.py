################################################################################
"""PyCEV Tests - Load a Trusted CEV and Verify Nothing Explodes."""
################################################################################
# pylint: disable=wrong-import-position, import-error

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load the pycev Package
import pycev

# Define the Path to CEV Files, and Load the Data from One Such File
cev_dir = os.path.join( os.getcwd(), 'test', 'cev-files' )
sel_351s_event = os.path.join( cev_dir, 'trusted-event-file.CEV' )
with open(sel_351s_event, encoding="utf-8") as f:
    relay_data = f.read()

def test_load_using_filepath_durring_init():
    """Parse in Constructor using File Path."""
    pycev.CEV(file=sel_351s_event)

def test_load_as_data_durring_init():
    """Parse in Constructor using Data from File."""
    pycev.CEV(data=relay_data)

def test_load_using_filepath():
    """Parse using Load with File Path."""
    cev_parser = pycev.Cev()
    cev_parser.load(file=sel_351s_event)

def test_load_as_data():
    """Parse using Load with Data from File."""
    cev_parser = pycev.Cev()
    cev_parser.load_data(data=relay_data)

# END
