"""
pycev: A compressed event record reader for SEL CEV files.

Author(s):
  - Joe Stanley: joe_stanley@selinc.com

Homepage: https://github.com/engineerjoe440/pycev

SEL Protocol Application Guide: https://selinc.com/api/download/5026/
SEL Compressed ASCII (CASCII) Application Guide: https://selinc.com/api/download/5021/
"""

# Standard Imports
import os
import time

# Local Imports

# Describe Package for External Interpretation
_name_ = "selcev"
_version_ = "0.0"
__version__ = _version_  # Alias the Version String


# Define the Primary Class
class Cev():
    """
    
    """
    
    def __init__(self, file=None, data=None, encoding=None):
        """
        Class initialization with optional data input methods for file-path
        and raw data as either a string or bytes.
        """
        if file is not None:
            if not os.path.exists( file ):
                raise ValueError("Argument `file` must be a valid file-path to a .CEV file.")
            else:
                self.load( file=file, encoding=encoding )
        elif data is not None:
            self.load_data( data=data, encoding=encoding )
    
    
    # Define File Loader Method
    def load(self, file, encoding=None):
        """
        
        """
    
    # Define Data Loader Method
    def load_data(self, data, encoding=None):
        """
        
        """