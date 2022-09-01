# PyCEV <img src="https://raw.githubusercontent.com/engineerjoe440/pycev/main/logo/pycev.png" width="250" alt="logo" align="right">
*Python interpreter for SEL (Schweitzer Engineering Laboratories) CEV (Compressed EVent record) files.*

[![PyPI Version](https://img.shields.io/pypi/v/pycev.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/pycev/)
[![Downloads](https://pepy.tech/badge/pycev)](https://pepy.tech/project/pycev)
[![Stars](https://img.shields.io/github/stars/engineerjoe440/pycev?logo=github)](https://github.com/engineerjoe440/pycev/)
[![License](https://img.shields.io/pypi/l/pycev.svg?color=blue)](https://github.com/engineerjoe440/pycev/blob/master/LICENSE.txt)


[![pytest-unit-tests](https://github.com/engineerjoe440/pycev/actions/workflows/pytest-unit-tests.yml/badge.svg)](https://github.com/engineerjoe440/pycev/actions/workflows/pytest-unit-tests.yml)
[![pydocstyle](https://github.com/engineerjoe440/pycev/actions/workflows/pydocstyle.yml/badge.svg)](https://github.com/engineerjoe440/pycev/actions/workflows/pydocstyle.yml)
[![pylint](https://github.com/engineerjoe440/pycev/actions/workflows/pylint.yml/badge.svg)](https://github.com/engineerjoe440/pycev/actions/workflows/pylint.yml)

##### Test Status
| **Branch** | **Status** |
|------------|------------|
| main       | [![Build Status](https://jenkins.stanleysolutionsnw.com/buildStatus/icon?job=PyCEV-Functional-Test%2Fmain)](https://jenkins.stanleysolutionsnw.com/job/PyCEV-Functional-Test/job/main/) |
| develop    | [![Build Status](https://jenkins.stanleysolutionsnw.com/buildStatus/icon?job=PyCEV-Functional-Test%2Fdevelop)](https://jenkins.stanleysolutionsnw.com/job/PyCEV-Functional-Test/job/develop/) |

***NOTE:*** This project is in VERY early stages of development and is nowhere near completion.

## Description
This project, `pycev`, is intended to provide a means to interpret and interact with SEL CEV files
for scientific analysis using common Python tools such as NumPy, Pandas, Matplotlib, and others.
This package provides a parser and manager system to load and interact with SEL Compressed Event
files. Potential avenues to explore for future development include a COMTRADE conversion tool to
allow CEV to COMTRADE conversions, or to write CEV files from raw data.

This project is largely developed by using reverse-engineering practices to interpret
the CEV files generated by SEL relays.

## Example Usage

```python
from pycev import CEV
# Load a file and parse, directly.
record = CEV(file="./event-report.cev")
print("Trigger time = {}s".format(record.trigger_time))
```

<a title="Fabián Alexis, CC BY-SA 3.0 &lt;https://creativecommons.org/licenses/by-sa/3.0&gt;, via Wikimedia Commons" href="https://commons.wikimedia.org/wiki/File:Antu_dialog-warning.svg"><img width="25px" alt="Antu dialog-warning" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Antu_dialog-warning.svg/512px-Antu_dialog-warning.svg.png"></a> **Caution**

***This project, although providing support for CEV files created by SEL, is not
sponsored, tested, or vetted in any way by Schweitzer Engineering Laboratories (SEL).
This project is authored and maintained as an open-source project. Testing is performed
on a very small set of event records provided from hardware running in the author's
basement in the author's basement. In short, this project has no association with SEL.***

*Since this project is not rigorously tested across all SEL devices or in a wide variety
of use-cases, any time this project is used, it should first be thoroughly tested. This
project is not intended to serve protection-class systems in any capacity. It should
primarily be used for research, exploration, and other learning objectives.*

## Installation

**From PyPI as a Python Package**

Just go ahead and issue: `pip install pycev`

**From GitHub as a Python Package**

To install `pycev` from GitHub:

1. Download the repository as a zipped package.
2. Unzip the repository.
3. Open a terminal (command-prompt) and navigate to the new folder that's been unzipped.
(*Hint:* Use `cd <the-path-to-the-folder-you-unzipped-in>/pycev`)
4. Use `pip` or `python` to install with the following commands, respectively:
    - `$ pip install .`
    - `$ python setup.py install`
5. Verify that it's been installed by opening a Python instance and importing:
    `>>> import pycev` If no errors arise, the package has been installed.

**From GitHub as a Standalone File**

If you wish to use `pycev` as a standalone file in your Python project, you can simply
download the `pycev.py` file from GitHub (you'll want
[this file](https://github.com/engineerjoe440/pycev/blob/main/pycev/pycev.py) exactly)
and save it wherever you need it! Then, just `import pycev` and away you go!

## Contributing

Want to get involved? We'd love to have your help!

Please help us by identifying any issues that you come across. If you find an error,
bug, or just have questions, jump over to the
[issue](https://github.com/engineerjoe440/pycev/issues) page.

If you want to add features, or contribute yourself, feel free to open a pull-request.

#### Running Tests Locally

To run tests locally, [`pytest`](https://docs.pytest.org/en/7.1.x/) is required,
then you may simply run the command:

```shell
$ pytest tests/unit
```

Not all tests can be run, locally, since the functional tests require additional
resources provided by a Jenkins runner managed by Joe Stanley.

### Contact Info
:information_source: *As mentioned in the
[caution](https://github.com/engineerjoe440/pycev#warning-caution) above, this
project is not associated with Schweitzer Engineering Laboratories (SEL) in any
way, and as such, all contacts for questions, support, or other items should be
directed to the resources listed here.*

For issues found in the source code itself, please feel free to open an
[issue](https://github.com/engineerjoe440/pycev/issues), but for general inquiries
and other contact, feel free to address Joe Stanley.

- [engineerjoe440@yahoo.com](mailto:engineerjoe440@yahoo.com)
