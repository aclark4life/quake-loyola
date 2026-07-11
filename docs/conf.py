"""Sphinx configuration for quake-loyola."""

import os
import sys

# Make the package (src/quake_loyola) and generate_map.py (repo root) importable
# without installing them
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("../src"))

# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------
project = "quake-loyola"
copyright = "2026, Alex Clark"
author = "Alex Clark"

# ---------------------------------------------------------------------------
# Extensions
# ---------------------------------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",  # Pull docstrings from the source modules
    "sphinx.ext.napoleon",  # Google / NumPy docstring styles
    "sphinx.ext.viewcode",  # Links to highlighted source code
    "sphinx.ext.intersphinx",  # Cross-links to Python stdlib docs
]

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# ---------------------------------------------------------------------------
# autodoc settings
# ---------------------------------------------------------------------------
autodoc_member_order = "bysource"
autodoc_typehints = "description"
add_module_names = False

# ---------------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------------
html_theme = "furo"
html_title = "quake-loyola"
