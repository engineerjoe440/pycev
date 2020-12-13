.. pycev documentation master file


PYCEV: SEL Compessed EVent Record Reader in Python
==================================================

`pycev`, is intended to provide a means to interpret and interact with SEL CEV files
for scientific analysis using common Python tools such as NumPy, Pandas, Matplotlib, and others.
This package provides a parser and manager system to load and interact with SEL Compressed Event
files. Potential avenues to explore for future development include a COMTRADE conversion tool to
allow CEV to COMTRADE conversions, or to write CEV files from raw data.

The CEV file format was developed by
`Schweitzer Engineering Laboratories <https://selinc.com/>`_ for use primarily with
protective electric relays, and other intelligent electronic devices, and is actively maintained.
CEV files, or Compressed EVent records, contain information relating to faults encountered on
electrical power systems. They are especially useful in post-event-analysis and for ongoing
system development.

Core Documentation
------------------

.. toctree::
   :maxdepth: 1
   
   pycev


Installation
~~~~~~~~~~~~

**From PyPI as a Python Package**

This information is yet to come, as `pycev` has yet to be published to PyPI at this time.

**From GitHub as a Python Package**

To install `pycev` from GitHub:

#. Download the repository as a zipped package.
#. Unzip the repository.
#. Open a terminal (command-prompt) and navigate to the new folder that's been unzipped.
   (*Hint:* Use `cd <the-path-to-the-folder-you-unzipped-in>/pycev`)
#. Use `pip` or `python` to install with the following commands, respectively:
    
    - `$> pip install .`
    - `$> python setup.py install`

#. Verify that it's been installed by opening a Python instance and importing:
    `>>> import pycev` If no errors arise, the package has been installed.

**From GitHub as a Standalone File**

If you wish to use `pycev` as a standalone file in your Python project, you can simply
download the `pycev.py` file from GitHub (you'll want
`this file <https://github.com/engineerjoe440/pycev/blob/main/pycev/pycev.py>`_ exactly)
and save it wherever you need it! Then, just `import pycev` and away you go!



Project Information
-------------------

For additional information related to this project, please refer to the links and materials
linked below.

License
~~~~~~~
This project (`pycev`) is distributed under the standard, MIT license. Users may download,
modify, distribute, and use for both personal and commercial applications. There is no
warranty, and the `pycev` project maintainer(s) may not be held liable in the terms
specified by the MIT license. 

Contact Info:
~~~~~~~~~~~~~

For issues found in the source code itself, please feel free to open an
`issue <https://github.com/engineerjoe440/pycev/issues>`_, but for general inquiries
and other contact, feel free to address `Joe Stanley <mailto:joe_stanley@selinc.com>`_.


Source Repository and Package Release (PyPI):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- GitHub: https://github.com/engineerjoe440/pycev
- PyPI: no-link-available-yet

