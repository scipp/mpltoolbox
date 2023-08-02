# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

import os
import sys

src = os.path.abspath("../src")
os.environ["PYTHONPATH"] = src
sys.path.insert(0, src)

# -- Project information -----------------------------------------------------

project = "mpltoolbox"
copyright = "2023, Scipp contributors"
author = "Neil Vaytet"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
    "nbsphinx",
    "sphinx_copybutton",
]

autodoc_typehints = "description"

autosummary_generate = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# source_suffix = ['.rst', '.md']
source_suffix = ".rst"
html_sourcelink_suffix = ""  # Avoid .ipynb.txt extensions in sources

# The master toctree document.
master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"
html_theme_options = {
    "logo_only": True,
    "repository_url": "https://github.com/scipp/mpltoolbox",
    "repository_branch": "main",
    "use_repository_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "show_toc_level": 2,
}
html_logo = "images/logo.png"
html_favicon = "images/favicon.ico"
