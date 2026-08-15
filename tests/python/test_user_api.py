"""Public Frame API: no scratch files, cages, ASE optional."""

from pathlib import Path

import pytest

from pydseams import CageScore, Frame, IceCounts, Trajectory, from_arrays, read

TRAJ = Path(__file__).resolve().parents[1] / "data" / "exampleTraj.lammpstrj"


def test_read_guesses_oxygen():
    frame = read(TRAJ)
    assert frame.n_atoms == 250
    assert frame.atom_type == 2


def test_chill_plus_no_tempdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    frame = read(TRAJ.resolve())
    counts = frame.chill_plus()
    assert isinstance(counts, IceCounts)
    assert counts.hexagonal == 65
    assert counts.cubic == 42
    assert counts.interfacial == 58
    assert counts.water == 85
    assert sum(counts.values()) == 250
    leftover = [p for p in tmp_path.iterdir() if p.name.startswith("dseams_")]
    assert leftover == []


def test_cages_seeded_on_mixed_water():
    frame = read(TRAJ, bonded="cutoff")
    score = frame.cages(seeded=True)
    assert isinstance(score, CageScore)
    assert score.n_ih == 0
    assert score.n_ic == 0
    assert score.n_water == frame.n_atoms


def test_trajectory_alias():
    assert Trajectory is Frame
    traj = Trajectory(str(TRAJ.resolve()))
    counts = traj.classify_chill_plus()
    assert counts["hexagonal"] == 65


def test_from_arrays_roundtrip_positions():
    src = read(TRAJ)
    frame = from_arrays(src.positions, src.box, numbers=[8] * src.n_atoms)
    assert frame.n_atoms == 250
    assert frame.positions[0] == src.positions[0]


def test_available_readers():
    from pydseams import available_readers

    readers = available_readers()
    assert readers["lammps"] is True
    assert "xyz" in readers


def test_read_xyz(tmp_path):
    xyz = tmp_path / "pair.xyz"
    xyz.write_text("2\n\nO 0.0 0.0 0.0\nO 1.0 0.0 0.0\n")
    frame = read(xyz)
    assert frame.n_atoms == 2


def test_to_solvis_optional():
    pytest.importorskip("solvis")
    from pydseams import to_solvis

    frame = read(TRAJ, bonded="cutoff")
    system = to_solvis(frame)
    assert len(system.atoms) == frame.n_atoms


def test_from_ase_optional():
    ase = pytest.importorskip("ase")
    from ase import Atoms
    from pydseams import from_ase

    src = read(TRAJ)
    atoms = Atoms(
        symbols=["O"] * src.n_atoms,
        positions=src.positions,
        cell=src.box,
        pbc=True,
    )
    frame = from_ase(atoms, select="O", bonded="cutoff")
    assert frame.n_atoms == 250
    back = frame.to_ase()
    assert len(back) == 250
    assert back.get_chemical_symbols()[0] == "O"
