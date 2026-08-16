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
    assert counts.interClathrate == 12
    assert counts.water == 238
    assert counts.cubic == 0
    assert counts.hexagonal == 0
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
    assert counts["hexagonal"] == 0
    assert counts["water"] == 238
    assert counts["interClathrate"] == 12


def test_from_arrays_roundtrip_positions():
    src = read(TRAJ)
    frame = from_arrays(src.positions, src.box, numbers=[8] * src.n_atoms)
    assert frame.n_atoms == 250
    assert frame.positions[0] == src.positions[0]


def test_frame_rdf_two_type(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    positions = [
        [0.0, 0.0, 0.0],
        [2.8, 0.0, 0.0],
        [0.0, 2.8, 0.0],
        [2.8, 2.8, 0.0],
    ]
    frame = from_arrays(
        positions, [30.0, 30.0, 30.0], numbers=[1, 2, 1, 2]
    )
    r, g = frame.rdf(1, 2)
    nbin = int(12.0 / 0.05)
    assert len(r) == nbin
    assert len(g) == nbin
    assert any(gi > 0 for gi in g)
    leftover = [p for p in tmp_path.iterdir() if p.name.startswith("dseams_")]
    assert leftover == []


def test_frame_cn_matches_unlike_degree():
    positions = [
        [0.0, 0.0, 0.0],
        [2.8, 0.0, 0.0],
        [0.0, 2.8, 0.0],
        [2.8, 2.8, 0.0],
    ]
    frame = from_arrays(positions, [30.0, 30.0, 30.0], numbers=[1, 2, 1, 2])
    assert frame.cn(1, 2, cutoff=3.0, binwidth=0.1) == pytest.approx(1.0)
    assert frame.cn(1, 2, cutoff=1.0, binwidth=0.1) == pytest.approx(0.0)


def test_site_table_type_one_is_not_chemistry():
    from pydseams import yoda

    table = yoda.parseSiteSpec("2=anion")
    assert table.ofType(1) == yoda.SiteKind.unspecified
    assert table.ofType(2) == yoda.SiteKind.anion


def test_ion_cloud_two_atom_com():
    from pydseams import yoda

    positions = [[0.5, 0.0, 0.0], [9.5, 0.0, 0.0]]
    frame = from_arrays(positions, [10.0, 10.0, 10.0], numbers=[1, 1])
    frame.cloud.pts[0].molID = 7
    frame.cloud.pts[0].atomID = 1
    frame.cloud.pts[1].molID = 7
    frame.cloud.pts[1].atomID = 2
    table = yoda.parseSiteSpec("1=cationHead")
    ions = frame.ion_cloud(table)
    assert ions.nop == 1
    assert ions.pts[0].c_type == 1
    assert ions.pts[0].x == pytest.approx(0.0)


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
    pytest.importorskip("ase")
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
