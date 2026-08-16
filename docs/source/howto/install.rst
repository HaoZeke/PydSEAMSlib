================
Install pydseams
================

Problem
=======

You want ``import pydseams`` in a working interpreter, with optional
ASE or solvis extras.

Requirements
============

- Python 3.12+
- pip or pixi

Wheels are the CPython 3.12 limited ABI (one ``abi3`` wheel per
platform). A wheel already links the d-SEAMS engine. Do not compile
``yoda`` to install the package.

pip
===

.. code-block:: bash

   pip install pydseams
   pip install 'pydseams[ase]'
   pip install 'pydseams[solvis]'

======================================= =================================
extra                                   provides
======================================= =================================
``pip install pydseams``                ``Frame``, ``read``, ``yoda``
``pip install 'pydseams[ase]'``         ``from_ase``, ``Frame.to_ase``
``pip install 'pydseams[solvis]'``      ``to_solvis`` (pulls ASE)
======================================= =================================

The ``[solvis]`` extra installs ASE as well. Without an extra,
``from_ase`` / ``to_ase`` / ``to_solvis`` raise ``ImportError`` and
name the matching ``pip install`` command.

pixi
====

Add the PyPI package to a pixi project:

.. code-block:: bash

   pixi add --pypi pydseams

Extras:

.. code-block:: bash

   pixi add --pypi 'pydseams[ase]'
   pixi add --pypi 'pydseams[solvis]'

Verify
======

.. code-block:: bash

   python -c "import pydseams as ds; print(ds.__version__); print(ds.yoda is ds._core)"

The first line prints the installed version. The second line prints
``True``: ``_core`` and ``cyoda`` are aliases of ``yoda``.

``import pydseamslib`` is a compatibility alias of ``pydseams``.

From a checkout
===============

Nix, at the repository root:

.. code-block:: bash

   nix build
   nix develop

``nix build`` produces the ``pydseams`` package. ``nix develop`` is
the dev shell (pytest, hypothesis).

This is the checkout path. The published wheel is the install path
for the docs site and for application code.

Next steps
==========

- :doc:`../quickstart` : classify one frame
- :doc:`../tutorials/classify-ice` : fixture dump
- :doc:`faq` : names and extras
