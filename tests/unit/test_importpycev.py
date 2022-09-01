################################################################################
"""PyCEV Tests - Import PyCEV Just to Verify No Major Issues."""
################################################################################
# pylint: disable=unused-import, import-error, import-outside-toplevel

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import_by_name():
    """Import Package Directly."""
    import pycev

def test_import_as_package_module():
    """Import Module from Package."""
    from pycev import pycev

def test_import_primary_class_pascal_case():
    """Import Class from Module - Lowercase."""
    from pycev import Cev

def test_import_primary_class_uppercase():
    """Import Class from Module - Uppercase."""
    from pycev import CEV

# END
