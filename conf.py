# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from __future__ import annotations
import os
from pathlib import Path
try:
    from importlib.metadata import version as _pkg_version  # Python 3.8+
except Exception:  # pragma: no cover
    _pkg_version = None  # type: ignore

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore

project = 'PyQt6 MultiSelectComboBox'
copyright = '2025, user0706'
author = 'user0706'

# Figure out docs version with multiple strategies
_release = os.getenv('DOCS_VERSION_OVERRIDE') or '1.1.1'

# 1) Prefer installed package version if available
if _pkg_version is not None:
    try:
        _release = _pkg_version('pyqt6-multiselect-combobox')
    except Exception:
        pass

# 2) Fallback to pyproject.toml in repo
if (not _release or _release == '1.1.1'):
    root = Path(__file__).resolve().parent
    pyproject = root / 'pyproject.toml'
    if pyproject.exists() and tomllib is not None:
        try:
            with pyproject.open('rb') as f:
                data = tomllib.load(f)
            _release = data.get('project', {}).get('version', _release)
        except Exception:
            pass

release = _release
version = _release
html_title = 'PyQt6 MultiSelectComboBox'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
    'sphinx_design',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'venv', 'html', 'doctrees']

# Autosummary/Autodoc
autosummary_generate = True
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
# Mock heavy/GUI dependencies so RTD can import the package without a Qt backend
autodoc_mock_imports = ['PyQt6']

# Napoleon (Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_attr_annotations = True

# MyST (CommonMark/Markdown)
myst_enable_extensions = [
    'colon_fence',
    'deflist',
    'linkify',
]

# Intersphinx references
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', {}),
    'pyqt6': ('https://doc.qt.io/qtforpython-6/', {}),
}



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_favicon = "_static/logo.png"
html_logo = "_static/logo.svg"
html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
}
