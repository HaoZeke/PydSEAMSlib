# PydSEAMSlib

<p align="center">
  <img src="docs/source/_static/logo/pydseams-icon.png" alt="pydseams" width="96">
</p>

[![built with nix](https://builtwithnix.org/badge.svg)](https://builtwithnix.org)

Python bindings for the [d-SEAMS](https://dseams.info) C++ engine
([`seams-core`](https://github.com/d-SEAMS/seams-core)).

This repository is the Python package `pydseams`. The C++ engine and
`seams` CLI live in [`seams-core`](https://github.com/d-SEAMS/seams-core).
Lua/Fennel is `dseams` in [`yodaStruct`](https://github.com/d-SEAMS/yodaStruct).
Neighbour search is [`linkcell`](https://github.com/d-SEAMS/linkcell).
Do not grow a second engine here. `import pydseamslib` still works.

```bash
pip install pydseamslib
pip install 'pydseamslib[ase]'      # ASE Atoms
pip install 'pydseamslib[solvis]'   # solvis / PyVista
```

Nix flake:

```bash
nix build
nix develop
```

Docs: `docs/orgmode/` (ox-rst) and `docs/source/` (Shibuya).
Site: <https://d-seams.github.io/PydSEAMSlib/>.

```python
import pydseams as ds

frame = ds.read("water.lammpstrj")   # also .xyz, .pdb, .gro, .dcd, .con
print(frame.chill_plus())
print(frame.cages())
print(frame.density(bins=100, axis="z"))

sites = ds.yoda.parseSiteSpec("1=polar,2=apolar")
print(frame.domain(sites, ds.yoda.Kind.polar))

frame = ds.from_ase(atoms)
atoms = frame.to_ase()
system = frame.to_solvis()           # optional extra
```

`ds.read` picks the engine reader from the suffix. `yoda` is the compiled
surface. Helpers (`Frame`, `io`, ASE, solvis) stay in Python.
`_core` and `cyoda` still name the same module.

`Frame.density`, `Frame.pairs`, and `Frame.domain` expose the same
site-resolved density, ion-pair, and connected-domain analyses as the CLI.
ASE adapters accept nonsingular cells periodic in all three directions and
preserve cell orientation and displacement on roundtrip.

Cutoff, frame, and *k* follow the same twelve-factor table as
`seams`: `SEAMS_CONFIG` or `./seams.env`, then the environment, then
the function argument. `pydseams.config` is the reader.

Primary author: Ruhila S. The project started as PSF GSoC 2023 (`pyseams`).

Requires Python 3.12+. Wheels are built against the CPython 3.12 stable
ABI (one `abi3` wheel per platform). Free-threaded CPython has no
limited ABI and is not a target.

# License

[MIT](LICENSE).
