==================
Classify ASE Atoms
==================



Problem
-------

You have an ASE ``Atoms`` and want CHILL+ labels or cage flags on the
same configuration, then an ``Atoms`` back with those arrays.

Install the extra
-----------------

.. code:: bash

    pip install 'pydseams[ase]'

Without it, ``from_ase`` / ``to_ase`` raise ``ImportError`` and name that
command.

Classify ASE Atoms
------------------

.. code:: python

    import ase.io
    import pydseams as ds

    atoms = ase.io.read("water.lammpstrj", format="lammps-dump-text")
    frame = ds.from_ase(atoms)
    print(frame.chill_plus())
    labelled = frame.to_ase()

``from_ase`` is ``Frame.from_ase``. The cell must be orthorhombic.
``from_ase`` keeps oxygen by default (``select="O"``).

Select and bonding
------------------

Pass a symbol, an atomic number, or ``None`` (every atom):

.. code:: python

    frame = ds.from_ase(atoms, select="O")
    frame = ds.from_ase(atoms, select=8)
    frame = ds.from_ase(atoms, select=None)

``bonded="auto"`` uses hydrogen bonds when the ``Atoms`` include ``H``,
otherwise the cutoff neighbour list. Single-site models (mW) have
no hydrogens:

.. code:: python

    frame = ds.from_ase(atoms, select="O", bonded="cutoff")

``bonded`` is ``"auto"``, ``"hbond"``, or ``"cutoff"``. Hydrogens stay in a
side cloud so the analysed species remain the CHILL / ring
particles.

Labels on the way back
----------------------

``to_ase`` rebuilds an ``Atoms`` with the analysed positions and an
orthorhombic cell (``pbc=True``). After ``chill_plus`` / ``chill``,
``atoms.arrays["ice_type"]`` holds the per-atom names. After
``cages()``, ``atoms.arrays["hc"]`` and ``atoms.arrays["ddc"]`` hold the
last ``CageScore``. ``atoms.info["dseams_n_atoms"]`` is the analysed
particle count.

A frame loaded from a LAMMPS dump (no ASE symbols) uses ``O`` as the
fallback species.

See also
--------

`View a frame in solvis <solvis.rst>`_
    wraps the same ``Atoms``

`Classify ice <../tutorials/classify-ice.rst>`_
    ``read`` / ``chill_plus`` / ``cages``

`Troubleshooting <troubleshooting.rst>`_
    non-orthorhombic cell, missing H
