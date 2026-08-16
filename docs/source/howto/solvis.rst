======================
View a frame in solvis
======================



Problem
-------

You have a ``Frame`` and want a solvis ``System`` for a PyVista view.

Install the extra
-----------------

.. code:: bash

    pip install 'pydseams[solvis]'

The extra pulls ASE as well. Without it, ``to_solvis`` raises
``ImportError`` and names that command.

Wrap the frame
--------------

.. code:: python

    import pydseams as ds

    frame = ds.read("water.lammpstrj")
    system = frame.to_solvis()
    # or: system = ds.to_solvis(frame)

solvis wraps the same ``Atoms`` ``to_ase`` would return. Pass
``expand_box=False`` to turn off the solvis box expansion
(default ``True``).

Classify first if you want ice labels on the exported ``Atoms``:

.. code:: python

    frame.chill_plus()
    frame.cages()
    system = frame.to_solvis()

``to_ase`` writes ``arrays["ice_type"]`` after CHILL and
``arrays["hc"]`` / ``arrays["ddc"]`` after ``cages()``. solvis sees
those arrays on the wrapped ``Atoms``.

This is the visualization path. Interactive plots and screenshots
follow the `solvis examples <https://github.com/amritagos/solvis>`_
(PyVista; press ``q`` to close the window). OVITO is not required.

See also
--------

`Classify ASE Atoms <ase.rst>`_
    ``from_ase`` / ``to_ase``

`The yoda surface <../explanation/yoda-surface.rst>`_
    why the viewer stays in Python
