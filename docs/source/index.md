# pydseams

Python bindings for the [d-SEAMS](https://dseams.info) C++ engine.

`pydseams` is the package. The compiled module is `yoda`. Helpers
(`Frame`, `read`, ASE, solvis) sit on that surface.
`import pydseamslib` still works.

```python
import pydseams as ds

frame = ds.read("water.lammpstrj")
print(frame.chill_plus())
print(frame.cages())
```

The engine and `seams` CLI live in
[seams-core](https://github.com/d-SEAMS/seams-core). Lua is `dseams`
in [yodaStruct](https://github.com/d-SEAMS/yodaStruct).

Author the narrative in `docs/orgmode/` and export with
`emacs --batch --load export.el`.

```{toctree}
:maxdepth: 1
:caption: Getting Started

quickstart
```

```{toctree}
:maxdepth: 1
:caption: How-To

howto/ase
```

```{toctree}
:maxdepth: 2
:caption: Reference

reference/python
api
history
```
