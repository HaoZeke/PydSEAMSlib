# Quickstart

## Install

```bash
pip install pydseams
pip install 'pydseams[ase]'
pip install 'pydseams[solvis]'
```

`pydseams` is the package. The `[ase]` extra pulls ASE for `from_ase` /
`to_ase`. The `[solvis]` extra pulls ASE plus solvis-tools for
`to_solvis`.

From a PydSEAMSlib checkout:

```bash
nix build
nix develop
```

`nix build` produces the `pydseams` package. `nix develop` is the
dev shell (pytest, hypothesis).

Requires Python 3.12+. Wheels are the CPython 3.12 limited ABI (one
`abi3` wheel per platform).

`import pydseamslib` is a compatibility alias of `pydseams`.

## Classify a frame

```python
import pydseams as ds

frame = ds.read("water.lammpstrj")   # also .xyz, .pdb, .gro, .dcd, .con
print(frame.chill_plus())
print(frame.cages())
```

`ds.read` picks the engine reader from the suffix and returns a
`Frame`. Classification does not write files.

`yoda` is the compiled module. `_core` and `cyoda` are aliases of
`yoda`. Helpers (`Frame`, `read`, ASE, solvis) stay in Python.

ASE `Atoms`: `ds.from_ase(atoms)`. See the ASE how-to.
