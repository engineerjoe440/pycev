# PyCEV <img src="https://raw.githubusercontent.com/engineerjoe440/pycev/main/logo/pycev.png" width="250" alt="logo" align="right">
*Python interpreter for SEL (Schweitzer Engineering Laboratories) CEV (Compressed EVent record) files.*

[![](https://img.shields.io/pypi/v/pycev.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/pycev/)
[![](https://pepy.tech/badge/pycev)](https://pepy.tech/project/pycev)
[![](https://img.shields.io/github/stars/engineerjoe440/pycev?logo=github)](https://github.com/engineerjoe440/pycev/)
[![](https://img.shields.io/pypi/l/pycev.svg?color=blue)](https://github.com/engineerjoe440/pycev/blob/master/LICENSE.txt)
[![Build Status](http://jenkins.stanleysolutionsnw.com/buildStatus/icon?job=PyCEV-CI)](http://jenkins.stanleysolutionsnw.com/job/PyCEV-CI/)

***NOTE:*** This project is in VERY early stages of development and is nowhere near completion.

## Description:
This project, `pycev`, is intended to provide a means to interpret and interact with SEL CEV files
for scientific analysis using common Python tools such as NumPy, Pandas, Matplotlib, and others.
This package provides a parser and manager system to load and interact with SEL Compressed Event
files. Potential avenues to explore for future development include a COMTRADE conversion tool to
allow CEV to COMTRADE conversions, or to write CEV files from raw data.

## Installation:

**From PyPI as a Python Package**

Just go ahead and issue: `pip install pycev`

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

## Contributing:

Want to get involved? We'd love to have your help!

Please help us by identifying any issues that you come across. If you find an error,
bug, or just have questions, jump over to the
[issue](https://github.com/engineerjoe440/pycev/issues) page.

If you want to add features, or contribute yourself, feel free to open a pull-request.

### Contact Info:
For issues found in the source code itself, please feel free to open an
[issue](https://github.com/engineerjoe440/pycev/issues), but for general inquiries
and other contact, feel free to address Joe Stanley.

- [joe_stanley@selinc.com](mailto:joe_stanley@selinc.com)
