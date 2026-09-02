"""Per-frame features and per-molecule states."""

from pathlib import Path

import numpy as np
import pytest

from pydseams import Trajectory
from pydseams.features import (
    FEATURE_NAMES,
    STATE_IC,
    STATE_IH,
    STATE_MIXED,
    STATE_WATER,
    IceFeaturizer,
    count_frames,
    discretize_nmax,
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
    chill = sum(names[k] for k in FEATURE_NAMES if k.startswith("chill_") and k != "chill_max")
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
