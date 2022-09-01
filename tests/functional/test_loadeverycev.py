################################################################################
"""PyCEV Tests - Evaluate All CEV Files."""
################################################################################
# pylint: disable=wrong-import-position, import-error

import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load the pycev Package
import pycev

# Define the Path to CEV Files, and Load the Data from One Such File
cev_dir = os.path.join(os.getcwd(), 'pycev-test-ci', 'cev-files')
cev_file_list = [f for f in os.listdir(cev_dir) if os.path.isfile(f)]

# Test Each Available CEV file. The expectation is that many will fail due to
# invalid formatting (which we'll work on later)
@pytest.mark.xfail()
@pytest.mark.parametrize('cev_file', cev_file_list, ids=cev_file_list)
def test_load_every_cev_file(cev_file):
    """Load Every File."""
    if cev_file.upper().endswith('.CEV'):
        pycev.CEV(file=os.path.join(cev_dir, cev_file))

# END
