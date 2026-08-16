========
pydseams
========

.. image:: _static/logo/pydseams-logo-light.svg
   :alt: pydseams
   :width: 320px
   :align: center

.. grid:: 1 2 3 3
   :gutter: 2
   :padding: 1 1 0 0
   :class-container: sd-text-center

   .. grid-item-card:: Read
      :link: quickstart
      :link-type: doc
      :class-card: sd-shadow-sm

      Load a LAMMPS dump, XYZ, PDB, GRO, DCD, or eOn ``.con`` as a
      ``Frame``.

   .. grid-item-card:: Classify
      :link: tutorials/classify-ice
      :link-type: doc
      :class-card: sd-shadow-sm

      CHILL+ labels and HC / DDC cage scores on one frame.

   .. grid-item-card:: Bind
      :link: howto/ase
      :link-type: doc
      :class-card: sd-shadow-sm

      Round-trip ASE ``Atoms``. Optional solvis view of the same
      cloud.

About
=====

``pydseams`` is the Python package for the d-SEAMS engine. The compiled
module is ``yoda``. Helpers (``Frame``, ``read``, ASE, solvis) sit on
that surface. ``import pydseamslib`` still works.

The engine and the ``seams`` CLI live in
`seams-core <https://github.com/d-SEAMS/seams-core>`_. Lua is
``dseams`` in `yodaStruct <https://github.com/d-SEAMS/yodaStruct>`_.
This site documents the Python ``Frame`` API. The header *Ecosystem*
menu jumps to the engine docs and the Lua front end.

.. code-block:: python

   import pydseams as ds

   frame = ds.read("water.lammpstrj")
   print(frame.chill_plus())
   print(frame.cages())

Suite stack
===========

Python helpers sit on the compiled ``yoda`` module. The same
``libyodaLib`` engine backs the ``seams`` CLI and the Lua ``dseams``
module.

.. mermaid::

   flowchart TB
     subgraph engine["seams-core"]
       LIB[libyodaLib]
     end
     subgraph compiled["pydseams.yoda"]
       YODA[yoda]
       ALIAS["_core / cyoda"]
     end
     subgraph helpers["Python helpers"]
       READ[ds.read]
       FRAME[Frame]
       ASE[from_ase / to_ase]
       SOL[to_solvis]
     end
     CLI["seams CLI"]
     LUA["yodaStruct / dseams"]
     LIB --> YODA
     YODA --- ALIAS
     LIB --> CLI
     LIB --> LUA
     YODA --> READ
     YODA --> FRAME
     FRAME --> ASE
     FRAME --> SOL

Documentation structure
=======================

This documentation follows the `Diataxis <https://diataxis.fr/>`_
framework.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   quickstart

.. toctree::
   :maxdepth: 2
   :caption: Tutorials

   tutorials/index
   tutorials/classify-ice

.. toctree::
   :maxdepth: 2
   :caption: How-to

   howto/index
   howto/install
   howto/ase
   howto/solvis
   howto/faq
   howto/troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: Explanation

   explanation/index
   explanation/yoda-surface
   explanation/frame
   explanation/citation

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/index
   reference/python
   api

.. toctree::
   :maxdepth: 1
   :caption: Development

   history

Related projects
================

- `seams-core <https://github.com/d-SEAMS/seams-core>`_ :: ``libyodaLib`` and the ``seams`` CLI
- `yodaStruct <https://github.com/d-SEAMS/yodaStruct>`_ :: Lua / Fennel ``require("dseams")``
- `d-SEAMS engine docs <https://docs.dseams.info>`_ :: C++ API and theory
- `dseams.info <https://dseams.info>`_ :: project site

License
=======

MIT. Cite the 2020 d-SEAMS paper (DOI
`10.1021/acs.jcim.0c00031 <https://doi.org/10.1021/acs.jcim.0c00031>`_).
See :doc:`explanation/citation`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
