# Release Versioning Support Script
# Joe Stanley | 2021

import re
import requests

USERNAME = 'engineerjoe440'
REPO = 'pycev'

try:
    from pycev import pycev
except ImportError:
    import os, sys
    sys.path.insert(0, os.getcwd())
    from pycev import pycev

import requests

response = requests.get(f"https://api.github.com/repos/{USERNAME}/{REPO}/releases/latest")
try:
    latest = response.json()["name"]
    latest = re.findall(r'v\d\.\d\.\d', latest)[0]
except Exception:
    latest = '0.0.0'

# Verify Version is Newer
version = f"v{pycev.__version__}"
if version <= latest:
    raise ValueError(
        f"Module version ({version}) is not newer than previous release "
        f"({latest})!"
    )
else:
    print(version)