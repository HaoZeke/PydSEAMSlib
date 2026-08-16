=========
Why Frame
=========


CHILL, rings, cages, Steinhardt, and SOAP are per-snapshot. The
handle is one configuration: neighbours, a bonded graph, and labels
on that cloud. ``Frame.cages`` is the ice score (HC = Ih, DDC = Ic,
neither = water).

Cutoff neighbour lists (``neighbor_list``, CHILL, cutoff-graph
cages) go through vesin when the engine is built with it. The
default ice score (``cages(seeded=True)``) uses linkcell k-NN. Those
backends are not interchangeable.

Runtime knobs
-------------

``pydseams.config`` shares the engine twelve-factor table. Defaults
live in the module. ``SEAMS_CONFIG`` or ``./seams.env`` fills unset
keys. The process environment wins the file. Function arguments
win the environment. ``Frame`` reads ``SEAMS_FRAME`` and ``SEAMS_CUTOFF``
when those arguments are omitted.

One configuration
-----------------

``Frame`` is that handle. Multi-frame work is explicit:
``read(path, frame=n)`` (1-indexed) or ``frame.load_frame(n)`` on a
path-backed ``Frame``. Arrays-only and ASE-built frames have no path
and cannot ``load_frame``.

``Trajectory`` is an alias
--------------------------

``Trajectory`` is a compatibility alias of ``Frame``
(``src/pydseams/__init__.py``). It does not iterate a movie and does
not own a campaign. The engine CLI that walks trajectories and
writes ``output/`` lives in seams-core. This package does not grow a
second movie object.
