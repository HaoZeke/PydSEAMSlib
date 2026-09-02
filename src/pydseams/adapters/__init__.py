"""Adapters to trajectory and visualisation tools.

- :mod:`pydseams.adapters._mdanalysis` (``IceStates``): an MDAnalysis
  analysis over a trajectory.
- :mod:`pydseams.adapters._ovito` (``ice_states``): an OVITO modifier
  function that adds the ``Ice state`` particle property.
- :func:`to_frame`: the ASE path, kept for older scripts;
  :func:`pydseams.from_ase` is the current name.
"""

from pydseams.adapters._ase import to_frame
from pydseams.adapters._mdanalysis import IceStates
from pydseams.adapters._ovito import ice_states

__all__ = ["IceStates", "ice_states", "to_frame"]
