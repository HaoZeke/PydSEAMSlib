"""Per-frame features and per-molecule states."""

from pathlib import Path

import numpy as np
import pytest

from pydseams import Trajectory
from pydseams.features import (
    FEATURE_NAMES,
    ION_FEATURE_NAMES,
    ION_FRONT,
    ION_ICE,
    ION_LIQUID,
    STATE_IC,
    STATE_IH,
    STATE_MIXED,
    STATE_WATER,
    IceFeaturizer,
    count_frames,
    discretize_nmax,
    ion_environment,
)

TRAJ = Path(__file__).resolve().parents[1] / "data" / "exampleTraj.lammpstrj"


def test_features_are_consistent_counts():
    traj = Trajectory(str(TRAJ), frame=1, atom_type=2, cutoff=3.5)
    feat = IceFeaturizer(traj, ring_adjacent=True)
    x, states = feat.frame_features()
    names = dict(zip(FEATURE_NAMES, x))
    assert x.shape == (len(FEATURE_NAMES),)
    assert states.shape == (traj.n_atoms,)
    assert set(np.unique(states)) <= {STATE_WATER, STATE_IC, STATE_IH, STATE_MIXED}
    assert names["n_ice"] == names["n_ic"] + names["n_ih"] + names["n_mixed"]
    assert int((states != STATE_WATER).sum()) == names["n_ice"]
    assert names["n_max"] <= names["n_ice"]
    assert (names["n_clusters"] == 0) == (names["n_ice"] == 0)
    chill = sum(
        names[k] for k in FEATURE_NAMES if k.startswith("chill_") and k != "chill_max"
    )
    assert chill == traj.n_atoms
    # the mixed TIP4P example: CHILL+ finds interfacial clathrate, the cages find nothing
    assert names["n_ice"] == 0
    assert names["chill_interclathrate"] == 12


def test_transform_stacks_frames():
    traj = Trajectory(str(TRAJ), frame=1, atom_type=2, cutoff=3.5)
    n = count_frames(str(TRAJ))
    X, S = IceFeaturizer(traj).transform(range(1, n + 1))
    assert X.shape == (n, len(FEATURE_NAMES))
    assert S.shape == (n, traj.n_atoms)


def test_discretize_nmax_bins():
    states = discretize_nmax([0, 5, 20, 314, 900], edges=[1, 100, 314])
    assert states.tolist() == [0, 1, 1, 3, 3]


def _cubic_diamond(reps, bond=2.75):
    a = 4.0 * bond / np.sqrt(3.0)
    fcc = [(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)]
    basis = fcc + [(x + 0.25, y + 0.25, z + 0.25) for (x, y, z) in fcc]
    pos = [
        ((i + b[0]) * a, (j + b[1]) * a, (k + b[2]) * a)
        for i in range(reps)
        for j in range(reps)
        for k in range(reps)
        for b in basis
    ]
    return np.asarray(pos) % (reps * a), [reps * a] * 3


def test_ion_in_ice_sees_an_ice_shell():
    from pydseams.frame import Frame

    pos, cell = _cubic_diamond(4)
    numbers = [1] * len(pos)
    numbers[0] = 3  # a substitutional ion at a lattice site
    frame = Frame.from_arrays(pos, cell, numbers=numbers, cutoff=3.5)
    assert frame.atom_type == 1
    feat = IceFeaturizer(frame, ring_adjacent=True, chill=False, ion_types=(3,))
    x, states = feat.frame_features()
    names = dict(zip(feat.feature_names, x))
    assert list(feat.feature_names[-4:]) == list(ION_FEATURE_NAMES)
    water = np.array([p.c_type for p in frame.cloud.pts]) == 1
    # the vacancy costs at most its own rings: the rest of the lattice stays cubic
    assert (states[water] == STATE_IC).mean() > 0.9
    assert states[~water].tolist() == [STATE_WATER]
    ions, shell, fraction, ion_states = ion_environment(frame, states, (3,))
    assert ions.tolist() == [0]
    assert shell.tolist() == [4]
    assert fraction[0] == 1.0
    assert ion_states.tolist() == [ION_ICE]
    assert (
        names["n_ion_ice"] == 1
        and names["n_ion_front"] == 0
        and names["n_ion_liquid"] == 0
    )
    assert names["ion_shell_ice"] == 1.0


def test_ion_without_water_shell_is_liquid():
    from pydseams.frame import Frame

    pos, cell = _cubic_diamond(3)
    pos = np.vstack([pos, [[cell[0] / 2 + 0.3, 0.7, cell[2] / 2 + 0.2]]])
    numbers = [1] * (len(pos) - 1) + [4]
    frame = Frame.from_arrays(pos, cell, numbers=numbers, cutoff=3.5)
    states = np.zeros(len(pos), dtype=np.int8)
    ions, shell, fraction, ion_states = ion_environment(frame, states, (4,), cutoff=0.5)
    assert shell.tolist() == [0]
    assert ion_states.tolist() == [ION_LIQUID]
    assert ION_FRONT not in ion_states


def test_from_ase_sequence_select_keeps_ions_for_ion_environment():
    ase = pytest.importorskip("ase")
    from ase import Atoms

    from pydseams.frame import Frame

    pos, cell = _cubic_diamond(4)
    symbols = ["O"] * len(pos)
    symbols[5] = "Na"
    symbols[40] = "Cl"
    # a hydrogen far from everything, to be dropped by the selection
    atoms = Atoms(
        symbols + ["H"],
        positions=np.vstack([pos, [[0.3, 0.3, 0.3]]]),
        cell=cell,
        pbc=True,
    )
    frame = Frame.from_ase(atoms, select=("O", "Na", "Cl"), bonded="cutoff")
    assert frame.atom_type == 8
    assert frame.n_atoms == len(pos)
    types = sorted(set(p.c_type for p in frame.cloud.pts))
    assert types == [8, 11, 17]
    feat = IceFeaturizer(frame, chill=False, ion_types=(11, 17))
    x, states = feat.frame_features()
    names = dict(zip(feat.feature_names, x))
    ions, shell, fraction, ion_states = ion_environment(frame, states, (11, 17))
    assert sorted(ions.tolist()) == [5, 40]
    assert shell.tolist() == [4, 4]
    assert ion_states.tolist() == [ION_ICE, ION_ICE]
    assert names["n_ion_ice"] == 2
