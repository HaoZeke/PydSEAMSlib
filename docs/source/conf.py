# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))
autodoc_mock_imports = ["pydseams.yoda"]

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "pydseams"
release = "2.2.2"
copyright = "2023--present, d-SEAMS developers"
author = "Ruhila S"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# referenced my favourite [1]
extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "sphinx_contributors",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib.bibtex",
]
autosummary_generate = True

templates_path = ["_templates"]
exclude_patterns = []

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "shibuya"
html_title = "pydseams"
html_static_path = ["_static"]

html_theme_options = {
    "github_url": "https://github.com/d-SEAMS/PydSEAMSlib",
    "accent_color": "teal",
    "dark_code": True,
    "light_logo": "_static/logo/pydseams_logo_light.png",
    "dark_logo": "_static/logo/pydseams_logo_dark.png",
    "nav_links": [
        {
            "title": "Engine",
            "url": "https://docs.dseams.info",
            "external": True,
        },
        {
            "title": "Lua",
            "url": "https://github.com/d-SEAMS/yodaStruct",
            "external": True,
        },
    ],
}
# --- Plugin options

myst_enable_extensions = [
    "deflist",
    "fieldlist",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "dseams": ("https://docs.dseams.info", None),
}

bibtex_bibfiles = ["bibtex/pyseamsDocs.bib"]

# references
# [1] https://github.com/HaoZeke/openblas_buildsys_snips/blob/main/docs/source/conf.py
