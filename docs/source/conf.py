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
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_contributors",
    "sphinx_copybutton",
    "sphinx_design",
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

html_context = {
    "source_type": "github",
    "source_user": "d-SEAMS",
    "source_repo": "PydSEAMSlib",
    "source_version": "main",
    "source_docs_path": "/docs/source/",
}

html_theme_options = {
    "github_url": "https://github.com/d-SEAMS/PydSEAMSlib",
    "accent_color": "teal",
    "dark_code": True,
    "globaltoc_expand_depth": 1,
    "light_logo": "_static/logo/pydseamslib_logo_light.png",
    "dark_logo": "_static/logo/pydseamslib_logo_dark.png",
    "nav_links": [
        {
            "title": "Ecosystem",
            "children": [
                {
                    "title": "d-SEAMS engine",
                    "url": "https://docs.dseams.info",
                    "summary": "libyodaLib and the seams CLI",
                },
                {
                    "title": "pydseams",
                    "url": "https://d-seams.github.io/PydSEAMSlib/",
                    "summary": "Python Frame API on yoda",
                },
                {
                    "title": "dseams (Lua)",
                    "url": "https://d-seams.github.io/yodaStruct/",
                    "summary": "require(\"dseams\") and Fennel",
                },
            ],
        },
    ],
}

html_sidebars = {
    "**": [
        "sidebars/localtoc.html",
        "sidebars/repo-stats.html",
        "sidebars/edit-this-page.html",
    ],
}

html_baseurl = "https://d-seams.github.io/PydSEAMSlib/"

# --- Plugin options

myst_enable_extensions = [
    "deflist",
    "fieldlist",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "ase": ("https://wiki.fysik.dtu.dk/ase/", None),
    "dseams": ("https://docs.dseams.info", None),
    "luadseams": ("https://d-seams.github.io/yodaStruct/", None),
}

bibtex_bibfiles = ["bibtex/pyseamsDocs.bib"]

# references
# [1] https://github.com/HaoZeke/openblas_buildsys_snips/blob/main/docs/source/conf.py
