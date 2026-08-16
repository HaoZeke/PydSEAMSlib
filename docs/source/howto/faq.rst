==========================
Frequently asked questions
==========================


.. contents::


Names
-----

Why is the package ``pydseams`` and the module ``yoda``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pydseams`` is the Python package. ``yoda`` is the compiled nanobind
extension inside it. That is the 2020 compiled surface name
(``libyodaLib`` in seams-core). Helpers sit on ``yoda`` the way
application code sits on a C API.

See `The yoda surface <../explanation/yoda-surface.rst>`_.

What is ``pydseamslib``?
~~~~~~~~~~~~~~~~~~~~~~~~

A compatibility alias of ``pydseams``. ``import pydseamslib`` still
works. New code imports ``pydseams``.

What are ``_core`` and ``cyoda``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aliases of ``pydseams.yoda``. ``assert ds._core is ds.yoda`` and
``assert ds.cyoda is ds.yoda``. New code imports ``yoda``.
``pydseams.Trajectory`` is an alias of ``Frame``.

Do I compile ``yoda`` to use the package?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. ``pip install pydseams`` installs a wheel that already links the
engine. Compile only if you develop the bindings from a checkout
(``nix build`` / ``nix develop``).

Usage
-----

Which formats does ``ds.read`` accept?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suffix dispatch:

.. table::

    +-----------------------------------------------+--------------------------+
    | suffix                                        | constructor              |
    +===============================================+==========================+
    | ``.xyz``                                      | ``Frame.from_xyz``       |
    +-----------------------------------------------+--------------------------+
    | ``.con``                                      | ``Frame.from_con``       |
    +-----------------------------------------------+--------------------------+
    | ``.pdb``, ``.gro``, ``.dcd``                  | ``Frame.from_chemfiles`` |
    +-----------------------------------------------+--------------------------+
    | ``.lammpstrj``, ``.dump``, ``.lammps``, other | ``Frame.from_file``      |
    +-----------------------------------------------+--------------------------+

``available_readers()`` reports which optional C++ readers this build
linked (``xyz``, ``chemfiles``, ``readcon``). ``lammps`` is always present.

Does classification write files?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``chill_plus``, ``chill``, and ``cages`` do not write files. Prism,
monolayer, and RDF helpers do.

Why must the ASE cell be orthorhombic?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The engine box is three lengths ``[lx, ly, lz]``. ``from_ase`` rejects
a general cell.

How do I keep every atom, not just oxygen?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    frame = ds.from_ase(atoms, select=None)

Default ``select="O"``. A symbol or an atomic number keeps that
species.

How do I view a classified frame?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

solvis. ``pip install 'pydseams[solvis]'``, then ``frame.to_solvis()``.
That is the visualization path. See
`View a frame in solvis <solvis.rst>`_. OVITO is not required.

How do I cite this?
~~~~~~~~~~~~~~~~~~~

Cite the 2020 d-SEAMS paper. See
`How to cite <../explanation/citation.rst>`_.

Compatibility
-------------

Which Python versions are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 3.12+. Wheels are the CPython 3.12 limited ABI. Free-threaded
CPython has no limited ABI and is not a target.

How is this different from ``seams`` and Lua ``dseams``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Same engine, different front end. ``seams`` is the CLI in seams-core.
``require("dseams")`` is the Lua / Fennel module in yodaStruct.
``pydseams`` is the Python ``Frame`` API.

See also
--------

- `Install pydseams <install.rst>`_

- `Troubleshooting <troubleshooting.rst>`_

- `Classify ice <../tutorials/classify-ice.rst>`_
