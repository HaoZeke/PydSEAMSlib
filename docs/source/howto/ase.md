# ASE

Install the extra first:

```bash
pip install 'pydseams[ase]'
```

Without it, `from_ase` / `to_ase` raise `ImportError` and name that
command.

## Classify ASE Atoms

```python
import ase.io
import pydseams as ds

atoms = ase.io.read("water.lammpstrj", format="lammps-dump-text")
frame = ds.from_ase(atoms)
print(frame.chill_plus())
labelled = frame.to_ase()
```

`from_ase` is `Frame.from_ase`. The cell must be orthorhombic.

## Select and bonding

`from_ase` keeps oxygen by default (`select="O"`). Pass a symbol, an
atomic number, or `None` (every atom).

```python
frame = ds.from_ase(atoms, select="O")
frame = ds.from_ase(atoms, select=8)
frame = ds.from_ase(atoms, select=None)
```

`bonded="auto"` uses hydrogen bonds when the `Atoms` include `H`,
otherwise the cutoff neighbour list. Single-site models (mW) have no
hydrogens:

```python
frame = ds.from_ase(atoms, select="O", bonded="cutoff")
```

`bonded` is `"auto"`, `"hbond"`, or `"cutoff"`.

## Labels on the way back

`to_ase` rebuilds an `Atoms` with the analysed positions and an
orthorhombic cell. After `chill_plus` / `chill`, `atoms.arrays["ice_type"]`
holds the per-atom names. After `cages()`, `atoms.arrays["hc"]` and
`atoms.arrays["ddc"]` hold the last `CageScore`.

A frame loaded from a LAMMPS dump (no ASE symbols) uses `O` as the
fallback species.

## solvis

```bash
pip install 'pydseams[solvis]'
```

```python
system = frame.to_solvis()
# or: system = ds.to_solvis(frame)
```

solvis wraps the same `Atoms` `to_ase` would return. The extra pulls
ASE as well.
