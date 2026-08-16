===============
Troubleshooting
===============


.. contents::


Installation
------------

``ModuleNotFoundError: No module named 'pydseams'``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package is not installed in the active interpreter.

.. code:: bash

    python -c "import sys; print(sys.executable)"
    python -m pip install pydseams

``ImportError`` naming ``pip install 'pydseams[ase]'``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ASE is not installed. The extra is optional:

.. code:: bash

    pip install 'pydseams[ase]'

``ImportError`` naming ``pip install 'pydseams[solvis]'``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

solvis-tools is not installed:

.. code:: bash

    pip install 'pydseams[solvis]'

Loading frames
--------------

``ValueError: ... has no atoms of type 1 or 2``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``Frame.from_file`` looks for LAMMPS type 2 (oxygen) then type 1.
The dump has neither, or ``atom_type`` does not match the file.
Pass ``atom_type`` explicitly, or use ``from_ase`` / ``from_arrays``
when the types are not 1/2.

``ValueError: from_ase needs an orthorhombic cell``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The engine box is three lengths. Make the ``Atoms`` cell
orthorhombic, or build the frame with ``from_arrays`` from
positions and ``[lx, ly, lz]``.

``ValueError: no atoms matched select=...``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``from_ase(..., select="O")`` found no oxygen. Pass the symbol or
atomic number that is present, or ``select=None``.

``ValueError: Hydrogen-bond analysis needs hydrogens``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``bonded="hbond"`` (or ``"auto"`` when the constructor decided
``hbond``) needs an H cloud. Pass ASE ``Atoms`` that include ``H``, a
LAMMPS dump with hydrogen, or set ``bonded="cutoff"``.

``RuntimeError: chemfiles is not linked in this build of seams-core``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``.pdb`` / ``.gro`` / ``.dcd`` need a wheel that linked chemfiles.
``available_readers()["chemfiles"]`` is ``False`` on this build.
Convert to LAMMPS or XYZ, or use a build with chemfiles.

``RuntimeError: readcon-core is not linked``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=.con~ needs a wheel that linked readcon-core.
``available_readers()["readcon"]`` reports the flag.

``RuntimeError: this build has no readXYZ``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=.xyz~ needs ``yoda.readXYZ``. Check ``available_readers()["xyz"]``.

Classification
--------------

Cage score is all water on a mixed snapshot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

That is the fixture result on
``tests/data/exampleTraj.lammpstrj``: CHILL+ sees local ice,
``cages()`` finds no finished HC or DDC. See the
`classify-ice tutorial <../tutorials/classify-ice.rst>`_.

Counts differ from a documented dump
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Confirm the path, the 1-indexed ``frame``, ``cutoff`` (default 3.5
Angstroms), and ``atom_type``. A different snapshot is a different
histogram.

Common messages
---------------

.. table::

    +--------------------------------------------+-------------------+------------------------------------+
    | Error                                      | Cause             | Action                             |
    +============================================+===================+====================================+
    | ``No module named 'pydseams'``             | Wrong interpreter | ``python -m pip install pydseams`` |
    +--------------------------------------------+-------------------+------------------------------------+
    | ``pip install 'pydseams[ase]'``            | ASE extra missing | install the extra                  |
    +--------------------------------------------+-------------------+------------------------------------+
    | ``orthorhombic cell``                      | General ASE cell  | three box lengths only             |
    +--------------------------------------------+-------------------+------------------------------------+
    | ``Hydrogen-bond analysis needs hydrogens`` | No H cloud        | ``bonded="cutoff"`` or pass H      |
    +--------------------------------------------+-------------------+------------------------------------+
    | ``chemfiles is not linked``                | Optional reader   | check ``available_readers()``      |
    +--------------------------------------------+-------------------+------------------------------------+

Getting help
------------

1. `FAQ <faq.rst>`_

2. `Python surface <../reference/python.rst>`_

3. `PydSEAMSlib <https://github.com/d-SEAMS/PydSEAMSlib>`_ issues

Include the ``pydseams`` version, Python version, the file suffix,
and the exact traceback.
