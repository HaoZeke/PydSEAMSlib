"""d-SEAMS Python front end.

Load a frame and ask for ice::

    import pydseams as ds
    frame = ds.read("water.lammpstrj")
    print(frame.chill_plus())
    print(frame.cages())

ASE Atoms work the same way::

    frame = ds.from_ase(atoms)          # default: oxygen
    atoms = frame.to_ase()
"""

from . import _core
from . import _core as cyoda
from .frame import CageScore, Frame, IceCounts, read
from .io import available_readers

__version__ = "2.2.0"

# Drop-in name used in the 2.0 docs and tests
Trajectory = Frame


def from_ase(atoms, select="O", cutoff=3.5, bonded="auto"):
    """Build a Frame from an ASE Atoms. select is a symbol or atomic number."""
    return Frame.from_ase(atoms, select=select, cutoff=cutoff, bonded=bonded)


def from_arrays(positions, cell, numbers=None, cutoff=3.5, bonded="cutoff"):
    """Build a Frame from (N, 3) positions and three box lengths."""
    return Frame.from_arrays(
        positions, cell, numbers=numbers, cutoff=cutoff, bonded=bonded
    )


def from_chemfiles(path, frame=1, **kwargs):
    """Build a Frame through chemfiles (PDB, GRO, DCD, ...)."""
    return Frame.from_chemfiles(path, frame=frame, **kwargs)


def from_con(path, frame=1, **kwargs):
    """Build a Frame from an eOn .con file."""
    return Frame.from_con(path, frame=frame, **kwargs)


def from_xyz(path, **kwargs):
    """Build a Frame from an XYZ file."""
    return Frame.from_xyz(path, **kwargs)


def to_solvis(frame, expand_box=True):
    """solvis.System for a Frame. Optional extra."""
    from .solvis import to_solvis as _to

    return _to(frame, expand_box=expand_box)


__all__ = [
    "Frame",
    "Trajectory",
    "IceCounts",
    "CageScore",
    "read",
    "from_ase",
    "from_arrays",
    "from_chemfiles",
    "from_con",
    "from_xyz",
    "to_solvis",
    "available_readers",
    "_core",
    "cyoda",
    "__version__",
]
