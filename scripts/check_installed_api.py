"""Smoke-test the public API from an installed pydseamslib artifact."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import pydseams as ds
import pydseamslib


def _check_read() -> None:
    dump = """ITEM: TIMESTEP
0
ITEM: NUMBER OF ATOMS
2
ITEM: BOX BOUNDS pp pp pp
0 10
0 10
0 10
ITEM: ATOMS id mol type x y z
1 1 1 1.0 1.0 1.0
2 2 1 2.0 1.0 1.0
"""
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "frame.lammpstrj"
        path.write_text(dump, encoding="utf-8")
        frame = ds.read(path, bonded="cutoff")
    assert frame.n_atoms == 2
    assert frame.atom_type == 1


def _check_structural_workflows() -> None:
    frame = ds.from_arrays(
        [
            [1.0, 1.0, 1.0],
            [2.8, 1.0, 1.0],
            [1.0, 2.8, 1.0],
            [2.8, 2.8, 1.0],
        ],
        [12.0, 12.0, 12.0],
        numbers=[1, 1, 1, 1],
    )
    assert sum(frame.chill_plus().values()) == frame.n_atoms
    assert sum(frame.chill().values()) == frame.n_atoms
    assert frame.cages(seeded=False).n_water == frame.n_atoms
    radii, rdf = frame.rdf(1, 1, cutoff=4.0, binwidth=0.1)
    assert len(radii) == len(rdf) == 40
    assert frame.cn(1, 1, cutoff=3.0, binwidth=0.1) >= 0.0
    assert len(frame.running_cn(1, 1, cutoff=3.0, binwidth=0.1)) == 30
    density = frame.density(bins=3, axis="z")
    assert isinstance(density, ds.DensityProfile)
    assert len(density.centres) == len(density.rho) == 3


def _check_site_workflows() -> None:
    frame = ds.from_arrays(
        [
            [1.0, 0.0, 0.0],
            [2.0, 0.0, 0.0],
            [7.0, 0.0, 0.0],
            [8.0, 0.0, 0.0],
        ],
        [10.0, 10.0, 10.0],
        numbers=[1, 2, 2, 1],
    )
    table = ds.yoda.parseSiteSpec("1=cationHead,2=anion")
    assert frame.ion_cloud(table).nop == 4
    assert frame.pairs(table).count == 2
    domain = frame.domain(table, ds.yoda.Kind.polar, cutoff=1.1)
    assert domain.n == 4
    assert domain.largest == 2


def _check_ase() -> None:
    from ase import Atoms

    restricted = np.array(
        [
            [4.0, 0.0, 0.0],
            [1.0, 5.0, 0.0],
            [0.5, 1.5, 6.0],
        ]
    )
    angle = np.deg2rad(31.0)
    rotation = np.array(
        [
            [np.cos(angle), -np.sin(angle), 0.0],
            [np.sin(angle), np.cos(angle), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    cell = restricted @ rotation
    atoms = Atoms(
        symbols=["O", "Na"],
        scaled_positions=[[0.1, 0.2, 0.3], [0.7, 0.6, 0.5]],
        cell=cell,
        pbc=True,
    )
    frame = ds.from_ase(atoms, select=None, bonded="cutoff")
    restored = frame.to_ase()
    np.testing.assert_allclose(restored.cell.array, atoms.cell.array, atol=1.0e-12)
    np.testing.assert_allclose(restored.positions, atoms.positions, atol=1.0e-12)


def main() -> None:
    assert pydseamslib.__version__ == ds.__version__
    _check_read()
    _check_structural_workflows()
    _check_site_workflows()
    _check_ase()
    print(f"pydseamslib {ds.__version__}: installed API check passed")


if __name__ == "__main__":
    main()
