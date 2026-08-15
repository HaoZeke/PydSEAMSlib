# PydSEAMSlib

Python bindings for the [d-SEAMS](https://dseams.info) C++ engine
([`seams-core`](https://github.com/d-SEAMS/seams-core)).

This repository is the Python package. The C++ library lives in
[`seams-core`](https://github.com/d-SEAMS/seams-core). The Lua and Fennel
CLI lives in [`yodaStruct`](https://github.com/d-SEAMS/yodaStruct). Do
not grow a second engine here.

```bash
pip install pydseamslib
pip install 'pydseamslib[ase]'   # optional ASE
```

```python
import pydseamslib as ds

frame = ds.read("water.lammpstrj")
print(frame.chill_plus())
print(frame.cages())

frame = ds.from_ase(atoms)
atoms = frame.to_ase()
```

Primary author: Ruhila S. The project started as PSF GSoC 2023 (`pyseams`).

Requires Python 3.12+. Wheels are built against the CPython 3.12 stable
ABI (one `abi3` wheel per platform). Free-threaded CPython has no
limited ABI and is not a target.

# License

[MIT](LICENSE).
