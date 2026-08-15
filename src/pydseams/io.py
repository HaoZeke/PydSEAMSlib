"""Suffix dispatch onto the C++ readers.

The compiled module stays thin. This is the Python helper layer: pick
LAMMPS, XYZ, chemfiles, or readcon from the path, then return a Frame.
"""

from __future__ import annotations

from pathlib import Path

from .frame import Frame

_CHEMFILES = {".pdb", ".gro", ".dcd"}
_LAMMPS = {".lammpstrj", ".dump", ".lammps"}


def read(path, frame=1, **kwargs):
    """Load a frame. Format follows the suffix; kwargs go to Frame."""
    suffix = Path(path).suffix.lower()
    if suffix == ".xyz":
        return Frame.from_xyz(path, **kwargs)
    if suffix == ".con":
        return Frame.from_con(path, frame=frame, **kwargs)
    if suffix in _CHEMFILES:
        return Frame.from_chemfiles(path, frame=frame, **kwargs)
    return Frame.from_file(path, frame=frame, **kwargs)


def available_readers():
    """Which optional C++ readers this build linked."""
    from . import yoda

    return {
        "lammps": True,
        "xyz": hasattr(yoda, "readXYZ"),
        "chemfiles": hasattr(yoda, "readChemfiles"),
        "readcon": hasattr(yoda, "readCon"),
    }
