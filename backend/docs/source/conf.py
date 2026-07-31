# Add the project root to the Python path
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parents[2]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'app'))

from app import create_app

app = create_app()

ctx = app.app_context()
ctx.push()

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_sqlalchemy',
]

# autodoc2_package = [
#     str(BASE_DIR / 'app'),
# ]

# # AutoAPI settings
# autoapi_type = 'python'
# autoapi_dirs = [str(BASE_DIR / 'app')]
# autoapi_options = [
#     'members',
#     'undoc-members',
#     'show-inheritance',
#     'show-module-summary'
# ]
# autoapi_template_dir = "_templates/autoapi"

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MeepleStatsLocal'
copyright = '2026, Alex'
author = 'Alex'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']
exclude_patterns = []

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme' # 'alabaster'
html_static_path = ['_static']
