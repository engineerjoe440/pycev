# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import re
import sys
print("Build with:", sys.version)
parent_dir = os.path.dirname(os.getcwd())
initfile = os.path.join(parent_dir, 'pycev.py')
sys.path.insert(0,parent_dir)
print(parent_dir)
# Gather Version Information from Python File
with open(initfile) as fh:
    file_str = fh.read()
    name = re.search('_name_ = \"(.*)\"', file_str).group(1)
    ver = re.search('_version_ = \"(.*)\"', file_str).group(1)
    # Version Breakdown:
    # MAJOR CHANGE . MINOR CHANGE . MICRO CHANGE
    print("Sphinx HTML Build For:", name, "   Version:", ver)


# Verify Import
try:
    import pycev
except:
    print("Couldn't import `pycev` module!")
    sys.exit(9)


# -- Project information -----------------------------------------------------

project = 'pycev'
copyright = '2022, Joe Stanley'
author = 'Joe Stanley'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [ 
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'numpydoc',
    'sphinx_sitemap',
    'myst_parser',
]
autosummary_generate = True
numpydoc_show_class_members = True

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_material'
html_title = 'pycev'
html_logo  = '../logo/pycev_white.png'
html_favicon = '../logo/pycev_favicon.png'
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "searchbox.html"]
}

html_theme_options = {

    # Set the name of the project to appear in the navigation.
    'nav_title': 'PyCEV',

    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    'base_url': 'https://pycev.readthedocs.io/en/latest/',

    # Set the color and the accent color
    'theme_color': '#08385D',
    'color_primary': 'light-blue',
    'color_accent': 'blue',

    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/engineerjoe440/pycev/',
    'repo_name': 'pycev',

    # Set the leading text at the top of the index page and others
    "heroes": {
        "index": "<b><i>Compressed Event Record Reader for Python</i></b>",
    },

    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 2,
    # If False, expand all TOC entries
    'globaltoc_collapse': False,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']




# END