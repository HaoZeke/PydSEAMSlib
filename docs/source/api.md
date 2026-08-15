# API reference

The public Python surface is {class}`~pydseams.frame.Frame`,
{func}`~pydseams.io.read`, and the ASE helpers
({func}`~pydseams.from_ase`, {meth}`~pydseams.frame.Frame.to_ase`).
The compiled extension is nanobind {mod}`pydseams.yoda`.
`_core` and `cyoda` are aliases of `yoda`. `Trajectory` is an alias
of `Frame`.

Classification ({meth}`~pydseams.frame.Frame.chill_plus`,
{meth}`~pydseams.frame.Frame.cages`) does not write files. Prism,
monolayer, and RDF helpers do.

```{eval-rst}
.. automodule:: pydseams
   :members:
   :imported-members:
   :exclude-members: Frame, IceCounts, CageScore, read, available_readers, yoda, _core, cyoda
```

## Frame

```{eval-rst}
.. automodule:: pydseams.frame
   :members:
   :exclude-members: read
   :show-inheritance:
   :member-order: bysource
```

## I/O

```{eval-rst}
.. automodule:: pydseams.io
   :members:
   :member-order: bysource
```

## Compiled module (`pydseams.yoda`)

`yoda` is mocked in the Sphinx build (`autodoc_mock_imports`), so
automodule cannot list live signatures. The tables below are the
functions and types `Frame` and the I/O helpers call, taken from
`src/bindings.cpp`. Do not treat this as the full registration
list.

```{eval-rst}
.. automodule:: pydseams.yoda
   :members:
   :undoc-members:
```

### I/O

| name | role |
|------|------|
| `readLammpsTrjreduced` | Read a LAMMPS trajectory frame, keeping only atoms of the given type. |
| `readLammpsTrj` | Read a LAMMPS trajectory frame with all atom types. |
| `readLammpsTrjO` | Read a LAMMPS trajectory frame, keeping only oxygen atoms. |
| `readXYZ` | Read atom coordinates from an XYZ file. |
| `readChemfiles` | Read any trajectory format supported by chemfiles (PDB, GRO, DCD, ...). Linked when `SEAMS_HAS_CHEMFILES`. |
| `readCon` | Read a `.con` file (eOn saddle-point search trajectories). Linked when `SEAMS_HAS_READCON`. |

### Neighbours and hydrogen bonds

| name | role |
|------|------|
| `neighListO` | Build a full neighbour list for a single atom type within a cutoff. |
| `neighbourListByIndex` | Convert an atom-ID neighbour list to an index-based neighbour list. |
| `kNearestNeighbourList` | Exact k-nearest bonded graph, union- or mutually-symmetrized. |
| `populateHbonds` | Build the hydrogen-bond network from a trajectory and neighbour list. |
| `populateHbondsWithInputClouds` | Build hydrogen bonds from pre-loaded oxygen and hydrogen point clouds. |

### Rings and cages

| name | role |
|------|------|
| `ringNetwork` | Find all primitive (shortest-path) rings up to `maxDepth`. |
| `cageAffiliation` | Order-free per-ring cage classification: `(hc, ddc)` flag vectors. |
| `seededCageAffiliation` | Seeded (hysteresis) per-atom cage flags: strict-graph seeds, permissive-graph completion. |
| `RingUpdater` | Exact incremental primitive rings for a neighbour list. |
| `AffiliationUpdater` | Exact incremental per-ring cage classification for one frame. |

### CHILL / CHILL+

| name | role |
|------|------|
| `getCorrelPlus` | Compute CHILL+ bond-order correlations and classify bond types. |
| `getIceTypePlusNoPrint` | Classify each atom's ice type using CHILL+. Does not write a file. |
| `getIceTypePlus` | Classify each atom's ice type using CHILL+ and write to file. |
| `getCorrel` | Compute CHILL bond-order correlations and classify bond types. |
| `getIceTypeNoPrint` | Classify each atom's ice type using CHILL. Does not write a file. |
| `getIceType` | Classify each atom's ice type using CHILL and write to file. |

### Descriptors and topology

| name | role |
|------|------|
| `steinhardtQl` | Local and neighbour-averaged Steinhardt parameters of degree `orderL`. |
| `steinhardtQlVoronoi` | Voronoi facet-area weighted Steinhardt parameters. |
| `classifyTemplates` | IRA/Horn overlay onto FCC, HCP, BCC, and SC neighbour shells. |
| `soapSpectrum` | SOAP power spectrum of one particle. |
| `soapSpectrumAll` | SOAP power spectrum of every particle. |
| `voronoiFeatures` | `[q4, q6, q8]` for every particle from one Voronoi pass per order. |
| `prismAnalysis` | Prism identification on rings up to `maxDepth`; writes output. |
| `polygonRingAnalysis` | Classify rings in a quasi-2D monolayer and write output. |
| `rdf2Danalysis_AA` | 2D radial distribution function for identical atom types. |
| `LinearClassifier` | Linear classifier used by `Frame.fit_classifier`. |

### Types

| name | role |
|------|------|
| `PointCloudDouble` | Collection of points for a single frame, with box dimensions. |
| `PointDouble` | Per-particle data: coordinates, type, molecule ID, ice classification. |
| `SteinhardtQl` | Per-particle Steinhardt `ql` and neighbour-averaged `qlBar`. |
| `AtomStateType` | Per-atom ice phase classification from CHILL / CHILL+ / q6. |
