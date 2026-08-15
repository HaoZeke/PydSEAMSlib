# Quickstart

```bash
pip install pydseams
pip install 'pydseams[ase]'
pip install 'pydseams[solvis]'
```

Nix: `nix build` / `nix develop` in a PydSEAMSlib checkout.

Requires Python 3.12+. Wheels are the CPython 3.12 limited ABI.

```python
import pydseams as ds

frame = ds.read("water.lammpstrj")
print(frame.chill_plus())
print(frame.cages())
```

`ds.read` picks the engine reader from the suffix. `yoda` is the
compiled module. `_core` and `cyoda` are aliases of `yoda`.
