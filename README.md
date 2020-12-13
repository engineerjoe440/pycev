# PyCEV <img src="https://raw.githubusercontent.com/engineerjoe440/pycev/main/logo/pycev.png" width="250" alt="logo" align="right">
*Python interpreter for SEL (Schweitzer Engineering Laboratories) CEV (Compressed EVent record) files.*

***NOTE:*** This project is in VERY early stages of development and is nowhere near completion.

## Description:
This project, `pycev`, is intended to provide a means to interpret and interact with SEL CEV files
for scientific analysis using common Python tools such as NumPy, Pandas, Matplotlib, and others.
This package provides a parser and manager system to load and interact with SEL Compressed Event
files. Potential avenues to explore for future development include a COMTRADE conversion tool to
allow CEV to COMTRADE conversions, or to write CEV files from raw data.

## Installation:

**From PyPI as a Python Package**

This information is yet to come, as `pycev` has yet to be published to PyPI at this time.

**From GitHub as a Python Package**

To install `pycev` from GitHub:

1. Download the repository as a zipped package.
2. Unzip the repository.
3. Open a terminal (command-prompt) and navigate to the new folder that's been unzipped.
(*Hint:* Use `cd <the-path-to-the-folder-you-unzipped-in>/pycev`)
4. Use `pip` or `python` to install with the following commands, respectively:
    - `$> pip install .`
    - `$> python setup.py install`
5. Verify that it's been installed by opening a Python instance and importing:
    `>>> import pycev` If no errors arise, the package has been installed.

**From GitHub as a Standalone File**

If you wish to use `pycev` as a standalone file in your Python project, you can simply
download the `pycev.py` file from GitHub (you'll want
[this file](https://github.com/engineerjoe440/pycev/blob/main/pycev/pycev.py) exactly)
and save it wherever you need it! Then, just `import pycev` and away you go!

### Contact Info:
For issues found in the source code itself, please feel free to open an
[issue](https://github.com/engineerjoe440/pycev/issues), but for general inquiries
and other contact, feel free to address Joe Stanley.

- [joe_stanley@selinc.com](mailto:joe_stanley@selinc.com)
