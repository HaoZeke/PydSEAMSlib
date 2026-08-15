# ASE

```python
import ase.io
import pydseams as ds

atoms = ase.io.read("water.lammpstrj", format="lammps-dump-text")
frame = ds.from_ase(atoms)
print(frame.chill_plus())
labelled = frame.to_ase()
```

`from_ase` selects oxygen by default. Pass `bonded="cutoff"` for
single-site models (mW). Optional extra `pydseams[solvis]` builds a
solvis `System`.
