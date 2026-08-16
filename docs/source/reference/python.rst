==============
Python surface
==============

Human lookup of :class:`~pydseams.frame.Frame`,
:class:`~pydseams.frame.IceCounts`,
:class:`~pydseams.frame.CageScore`, :func:`~pydseams.io.read`, and
the ASE helpers. Napoleon autodoc of every signature is the
:doc:`../api` page.

Frame
=====

:class:`~pydseams.frame.Frame` is the one-frame handle. Load a
LAMMPS dump, an ASE ``Atoms``, or raw arrays, then call
:meth:`~pydseams.frame.Frame.chill_plus` or
:meth:`~pydseams.frame.Frame.cages`. Classification does not write
files. Prefer :func:`~pydseams.io.read`,
:meth:`~pydseams.frame.Frame.from_ase`, or
:meth:`~pydseams.frame.Frame.from_arrays` over constructing
``Frame`` by filename.

``Trajectory`` is an alias of ``Frame``.

Constructors
------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - name
     - role
   * - :meth:`~pydseams.frame.Frame.from_file`
     - LAMMPS dump; guesses type 2 then type 1
   * - :meth:`~pydseams.frame.Frame.from_ase`
     - ASE ``Atoms``; ``select="O"``
   * - :meth:`~pydseams.frame.Frame.from_arrays`
     - ``(N, 3)`` positions and three box lengths
   * - :meth:`~pydseams.frame.Frame.from_xyz`
     - XYZ via ``yoda.readXYZ``
   * - :meth:`~pydseams.frame.Frame.from_chemfiles`
     - PDB / GRO / DCD when chemfiles is linked
   * - :meth:`~pydseams.frame.Frame.from_con`
     - eOn ``.con`` when readcon-core is linked

Package-level aliases:
:func:`~pydseams.from_ase`, :func:`~pydseams.from_arrays`,
:func:`~pydseams.from_xyz`, :func:`~pydseams.from_chemfiles`,
:func:`~pydseams.from_con`.

Geometry and graphs
-------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - name
     - role
   * - :attr:`~pydseams.frame.Frame.n_atoms`
     - analysed particle count (``cloud.nop``)
   * - :attr:`~pydseams.frame.Frame.box`
     - orthorhombic box lengths ``[lx, ly, lz]``
   * - :attr:`~pydseams.frame.Frame.positions`
     - list of ``(x, y, z)``
   * - :attr:`~pydseams.frame.Frame.neighbor_list`
     - cutoff neighbour list (``yoda.neighListO``)
   * - :attr:`~pydseams.frame.Frame.hbonds`
     - hydrogen-bond neighbour list
   * - :attr:`~pydseams.frame.Frame.rings`
     - primitive rings up to size 6
   * - :meth:`~pydseams.frame.Frame.load_frame`
     - reload a later frame from the same file

Classification
--------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - name
     - role
   * - :meth:`~pydseams.frame.Frame.chill_plus`
     - CHILL+ ice labels; no files written
   * - :meth:`~pydseams.frame.Frame.chill`
     - CHILL ice labels; no files written
   * - :meth:`~pydseams.frame.Frame.classify_chill_plus`
     - alias of ``chill_plus``
   * - :meth:`~pydseams.frame.Frame.classify_chill`
     - alias of ``chill``
   * - :meth:`~pydseams.frame.Frame.cages`
     - HC / DDC membership (``seeded=True``, ``k=4``)

:meth:`~pydseams.frame.Frame.cages` with ``seeded=True`` is the
hysteresis construction. ``seeded=False`` is cutoff-graph
affiliation on this frame's six-rings.

Export and descriptors
----------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - name
     - role
   * - :meth:`~pydseams.frame.Frame.to_ase`
     - ASE ``Atoms``; needs ``pydseams[ase]``
   * - :meth:`~pydseams.frame.Frame.to_solvis`
     - solvis ``System``; needs ``pydseams[solvis]``
   * - :meth:`~pydseams.frame.Frame.steinhardt`
     - local and neighbour-averaged ``ql``
   * - :meth:`~pydseams.frame.Frame.soap`
     - SOAP power spectrum
   * - :meth:`~pydseams.frame.Frame.voronoi_features`
     - per-atom ``[q4, q6, q8]``

Prism, monolayer, and RDF helpers write engine output. See the
Frame autodoc on :doc:`../api`.

IceCounts
=========

:class:`~pydseams.frame.IceCounts` is the histogram returned by
:meth:`~pydseams.frame.Frame.chill_plus` and
:meth:`~pydseams.frame.Frame.chill`.

Keys are the ``AtomStateType`` names (``cubic``, ``hexagonal``,
``water``, ``interfacial``, ``clathrate``, ``interClathrate``,
``unclassified``, ``reCubic``, ``reHex``). Missing keys read as
``0`` via attribute access, so ``counts.cubic`` and
``counts["hexagonal"]`` are equivalent. ``repr`` omits zero-count
labels.

CageScore
=========

:class:`~pydseams.frame.CageScore` is the per-atom score returned
by :meth:`~pydseams.frame.Frame.cages`.

A molecule in an HC is ice Ih; a molecule in a DDC is ice Ic.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - name
     - role
   * - ``hc``
     - per-atom hexagonal-cage flag
   * - ``ddc``
     - per-atom double-diamond-cage flag
   * - :attr:`~pydseams.frame.CageScore.n_ih`
     - number of atoms flagged HC
   * - :attr:`~pydseams.frame.CageScore.n_ic`
     - number of atoms flagged DDC
   * - :attr:`~pydseams.frame.CageScore.n_water`
     - number of atoms in neither cage

read
====

:func:`~pydseams.io.read` is the suffix-dispatching loader.
:func:`~pydseams.io.available_readers` reports which compiled
readers this build linked.

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - suffix
     - constructor
   * - ``.xyz``
     - :meth:`~pydseams.frame.Frame.from_xyz`
   * - ``.con``
     - :meth:`~pydseams.frame.Frame.from_con`
   * - ``.pdb``, ``.gro``, ``.dcd``
     - :meth:`~pydseams.frame.Frame.from_chemfiles`
   * - ``.lammpstrj``, ``.dump``, ``.lammps``, other
     - :meth:`~pydseams.frame.Frame.from_file`

Common kwargs: ``frame`` (1-indexed), ``cutoff`` (Angstroms,
default 3.5), ``bonded`` (``"auto"``, ``"hbond"``, ``"cutoff"``),
``atom_type``, ``region``. ``bonded="auto"`` uses hydrogen bonds
when hydrogens are available.

Builds without chemfiles or readcon raise ``RuntimeError`` when
those suffixes are used.

ASE
===

:func:`~pydseams.from_ase` / :meth:`~pydseams.frame.Frame.from_ase`
build a ``Frame`` from an ASE ``Atoms``.
:meth:`~pydseams.frame.Frame.to_ase` is the inverse.

Install: ``pip install 'pydseams[ase]'``. The cell must be
orthorhombic. ``select`` is a symbol, an atomic number, or
``None`` (every atom). Default ``select="O"``.

``to_ase`` writes ``arrays["ice_type"]`` after CHILL and
``arrays["hc"]`` / ``arrays["ddc"]`` after ``cages()``. A frame
loaded from a LAMMPS dump (no ASE symbols) uses ``O`` as the
fallback species.

Implementation autodoc is the ASE helpers section of
:doc:`../api`. Walkthrough: :doc:`../howto/ase`.

:func:`~pydseams.to_solvis` wraps the same ``Atoms``. Install:
``pip install 'pydseams[solvis]'``.

Package names
=============

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - name
     - role
   * - ``pydseams``
     - Python package
   * - ``pydseamslib``
     - compatibility alias of ``pydseams``
   * - ``pydseams.yoda``
     - compiled registrations
   * - ``pydseams._core``
     - alias of ``yoda``
   * - ``pydseams.cyoda``
     - alias of ``yoda``
   * - ``pydseams.Trajectory``
     - alias of ``Frame``

Requires Python 3.12+. Wheels are the CPython 3.12 limited ABI.

``yoda`` names (mocked in the Sphinx build) are tabulated on the
:doc:`../api` page.
