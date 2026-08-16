================
The yoda surface
================


The package is ``pydseams``. The compiled extension inside it is
``yoda``. That split is deliberate.

The 2020 name
-------------

d-SEAMS shipped in 2020 as `yodaStruct <https://github.com/d-SEAMS/yodaStruct>`_
(Goswami, Goswami, Singh, *J. Chem. Inf. Model.* 2020,
DOI `10.1021/acs.jcim.0c00031 <https://doi.org/10.1021/acs.jcim.0c00031>`_).
The C++ library is still ``libyodaLib`` in
`seams-core <https://github.com/d-SEAMS/seams-core>`_. The Lua and Fennel
front end still lives in yodaStruct (``require("dseams")``).

The nanobind module is ``yoda`` because that is the 2020 compiled
surface name: ``NB_MODULE(yoda, ...)`` and Meson's
``extension_module('yoda', ..., subdir: 'pydseams')``. Importing
``pydseams.yoda`` is the same object the C++ engine always was.

The Python **package** is ``pydseams``, not ``yoda``. ``yoda`` is the
extension, the way ``libyodaLib`` is the engine and ``dseams`` is the
Lua module. ``import pydseamslib`` still works; that is the 2.0 /
repository name, re-exported from ``pydseams``.

Why helpers stay in Python
--------------------------

``yoda`` registers the engine: ``PointCloudDouble``, the readers,
neighbour lists, CHILL, rings, cages, Steinhardt, SOAP. It does not
own suffix dispatch, ASE ``Atoms``, or solvis. seams-core v2.4.0 also
has ``site::Table``, ``rdf::coordinationNumber``,
``populateHbondsFromDonors``, and ``neighListPair``; ``yoda`` still
exposes ``neighList``, ``populateHbonds``, and ``rdf2Danalysis_AA``.

``Frame``, ``read``, ``from_ase``, ``from_arrays``, ``from_xyz``,
``from_chemfiles``, ``from_con``, and ``to_solvis`` sit in Python on that
surface. The compiled ABI does not grow a second I/O layer. A new
reader extra or a viewer extra is a Python module plus an optional
dependency (``pydseams[ase]``, ``pydseams[solvis]``), not a bump of the
C++ module.

``ds.read`` looks at the suffix and calls the matching constructor.
``yoda.readLammpsTrjreduced`` and friends stay available for callers
that want the raw cloud.

The trade-off is a thin compiled surface and a small Python
adapter layer. Application code imports ``pydseams`` and uses
``Frame``. The ``seams`` CLI and Lua ``dseams`` stay in their own
repositories and share ``libyodaLib``.

Aliases of the same module
--------------------------

.. code:: python

    import pydseams as ds

    assert ds._core is ds.yoda
    assert ds.cyoda is ds.yoda

.. table::

    +-------------------------+-----------------------------------------+
    | name                    | role                                    |
    +=========================+=========================================+
    | ``pydseams.yoda``       | compiled module (canonical)             |
    +-------------------------+-----------------------------------------+
    | ``pydseams._core``      | same object; 2.1 helper-layer name      |
    +-------------------------+-----------------------------------------+
    | ``pydseams.cyoda``      | same object; older compiled-module name |
    +-------------------------+-----------------------------------------+
    | ``pydseamslib``         | package alias of ``pydseams``           |
    +-------------------------+-----------------------------------------+
    | ``pydseams.Trajectory`` | alias of ``Frame``                      |
    +-------------------------+-----------------------------------------+

``_core`` is the private-looking name used when the helpers first sat
on the compiled surface. ``cyoda`` is the older import kept so
``from pydseams import cyoda`` still resolves. New code imports
``yoda``.
