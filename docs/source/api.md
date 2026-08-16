# API reference

Napoleon autodoc of the Python helpers. Human lookup of
{class}`~pydseams.frame.Frame`, {class}`~pydseams.frame.IceCounts`,
{class}`~pydseams.frame.CageScore`, {func}`~pydseams.io.read`, and
ASE is the [Python surface](reference/python) page.

The public constructors live on the {mod}`pydseams` package:
{func}`~pydseams.from_ase`, {func}`~pydseams.from_arrays`,
{func}`~pydseams.from_xyz`, {func}`~pydseams.from_chemfiles`,
{func}`~pydseams.from_con`, {func}`~pydseams.to_solvis`.
{meth}`~pydseams.frame.Frame.to_ase` is the inverse of
{func}`~pydseams.from_ase`.

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

## ASE helpers

Implementation of {func}`~pydseams.from_ase` and
{meth}`~pydseams.frame.Frame.to_ase`. Optional extra:
`pip install 'pydseams[ase]'`.

```{eval-rst}
.. automodule:: pydseams.aseio
   :members:
   :member-order: bysource
```

## solvis

Implementation of {func}`~pydseams.to_solvis` and
{meth}`~pydseams.frame.Frame.to_solvis`. Optional extra:
`pip install 'pydseams[solvis]'`.

```{eval-rst}
.. automodule:: pydseams.solvis
   :members:
   :member-order: bysource
```

## Compiled module (`pydseams.yoda`)

`yoda` is mocked in the Sphinx build (`autodoc_mock_imports`), so
automodule cannot list live signatures. The tables below are every
public name registered in `src/bindings.cpp`: 111 names (98
functions, 13 types). Four functions are compile-gated and absent
from builds that did not link the extra:
`readChemfiles` (`SEAMS_HAS_CHEMFILES`), `readCon`
(`SEAMS_HAS_READCON`), `ira_match` and `sofi_point_group`
(`SEAMS_HAS_IRA`).

Application code uses {class}`~pydseams.frame.Frame` /
{func}`~pydseams.io.read` / {func}`~pydseams.from_ase`. Call `yoda`
directly for the raw engine.

```{eval-rst}
.. automodule:: pydseams.yoda
   :members:
   :undoc-members:
```

### I/O

| name | role |
|------|------|
| `readXYZ` | Read atom coordinates from an XYZ file. |
| `readLammpsTrjreduced` | Read a LAMMPS trajectory frame, keeping only atoms of the given type. |
| `readLammpsTrjO` | Read a LAMMPS trajectory frame, keeping only oxygen atoms. |
| `readLammpsTrj` | Read a LAMMPS trajectory frame with all atom types. |
| `readBonds` | Read bond connectivity from a formatted bond file. |
| `atomInSlice` | Check whether a point `(x, y, z)` lies within a volume slice. |
| `readChemfiles` | Read any trajectory format supported by chemfiles (PDB, GRO, DCD, ...). Linked when `SEAMS_HAS_CHEMFILES`. |
| `readCon` | Read a `.con` file (eOn saddle-point search trajectories). Linked when `SEAMS_HAS_READCON`. |
| `writeDump` | Write a LAMMPS dump file for the current point cloud. |

### Neighbours and hydrogen bonds

| name | role |
|------|------|
| `clearNeighbourList` | Free memory for a neighbour list. |
| `getNewNeighbourListByIndex` | Build a neighbour list by index using a distance cutoff. |
| `kNearestNeighbourList` | Exact k-nearest bonded graph, union- or mutually-symmetrized. |
| `shellSeparation` | Certificate pair (max k-th distance, min (k+1)-th distance) for the exact reduction of the k-nearest graph to a cutoff graph. |
| `halfNeighList` | Build a half neighbour list (each pair stored once) for one atom type. |
| `neighbourListByIndex` | Convert an atom-ID neighbour list to an index-based neighbour list. |
| `neighList` | Build a full neighbour list for two atom types within a cutoff. |
| `neighListO` | Build a full neighbour list for a single atom type within a cutoff. |
| `createBondsFromCages` | Create bond connectivity from rings and cage information. |
| `getHbondDistanceOH` | Compute the O-H hydrogen bond distance between two atoms. |
| `populateHbonds` | Build the hydrogen-bond network from a trajectory and neighbour list. |
| `populateHbondsWithInputClouds` | Build hydrogen bonds from pre-loaded oxygen and hydrogen point clouds. |
| `trimBonds` | Remove duplicate bonds from a bond list. |

seams-core v2.4.0 also has `site::Table`, `rdf::coordinationNumber`,
`populateHbondsFromDonors`, and `neighListPair`. pydseams still uses
`neighList`, `populateHbonds`, and `rdf2Danalysis_AA`; those new
symbols are not bound.

### Rings and cages

| name | role |
|------|------|
| `clearGraph` | Free memory for a graph object. |
| `countAllRingsFromIndex` | Find all possible rings (including non-shortest-path) up to `maxDepth`. |
| `ringNetwork` | Find all primitive (shortest-path) rings up to `maxDepth`. |
| `cageAffiliation` | Order-free per-ring cage classification: `(hc, ddc)` flag vectors. |
| `seededCageAffiliation` | Seeded (hysteresis) per-atom cage flags: strict-graph seeds, permissive-graph completion. |
| `RingUpdater` | Exact incremental primitive rings for a neighbour list. |
| `AffiliationUpdater` | Exact incremental per-ring cage classification for one frame. |
| `populateGraphFromIndices` | Create a graph object from an index-based neighbour list. |
| `populateGraphFromNListID` | Create a graph object from an atom-ID neighbour list and point cloud. |
| `removeNonSPrings` | Remove non-shortest-path rings using the Franzblau criterion. |
| `restoreEdgesFromIndices` | Restore graph edges from an index-based neighbour list. |

### Ring classification

| name | role |
|------|------|
| `assignPolygonType` | Assign atom types based on the ring size of n-membered rings. |
| `assignPrismType` | Assign atom types for atoms belonging to prism rings. |
| `clearRingList` | Free memory for a list of rings. |
| `compareRings` | Check whether two unordered rings contain the same elements. |
| `commonElementsInThreeRings` | Check whether three rings share at least one common element. |
| `deformedPrismTypes` | Get atom type values for deformed prisms. |
| `discardExtraTetragonBlocks` | Discard duplicate 4-membered ring pairs that are parallel in one dimension. |
| `findPrisms` | Identify which rings form prism blocks. |
| `findsCommonElements` | Return the common elements shared by two rings. |
| `findTripletInRing` | Search for a triplet of atoms within a ring. |
| `getSingleRingSize` | Extract rings of a specific size from a list of all rings. |
| `hasCommonElements` | Check whether two rings share any common elements. |
| `basalPrismConditions` | Test whether two rings satisfy strict basal prism conditions. |
| `relaxedPrismConditions` | Test whether two rings satisfy relaxed prism conditions (at least one bond). |
| `getEdgeMoleculesInRings` | Select edge molecules in rings that straddle the slice boundary. |
| `printSliceGetEdgeMoleculesInRings` | Select edge molecules in rings and write slice output files. |

### Topology writers

| name | role |
|------|------|
| `polygonRingAnalysis` | Classify rings in a quasi-2D monolayer and write output. |
| `bulkPolygonRingAnalysis` | Classify rings in a bulk system and write output. |
| `prismAnalysis` | Prism identification on rings up to `maxDepth`; writes output. |
| `rmAxialTranslations` | Remove axial translations from an ice nanotube for visualization. |

### Topological unit matching

| name | role |
|------|------|
| `atomsFromCages` | Get atom indices belonging to cages in a given cluster. |
| `averageRMSDatom` | Average the per-atom RMSD over the number of shared cages. |
| `buildRefDDC` | Build a reference double-diamond cage from a template XYZ file. |
| `buildRefHC` | Build a reference hexagonal cage from a template XYZ file. |
| `clusterCages` | Cluster cages using Stillinger's algorithm and write XYZ output. |
| `shapeMatchDDC` | Shape-match a target double-diamond cage against a reference. |
| `shapeMatchHC` | Shape-match a target hexagonal cage against a reference. |
| `topoBulkCriteria` | Find HCs and DDCs in a bulk system using topological criteria. |
| `topoUnitMatchingBulk` | Run full topological unit matching for bulk water. |
| `updateRMSDatom` | Update per-atom RMSD from a cage shape-matching result. |

### Selection

| name | role |
|------|------|
| `getPointCloudOneAtomType` | Extract a point cloud containing only atoms of a given type. |
| `atomsInSingleSlice` | Mark atoms inside a rectangular volume slice. |
| `moleculesInSingleSlice` | Mark whole molecules as in-slice if any atom is inside the region. |
| `setAtomsWithSameMolID` | Set the `inSlice` flag for all atoms sharing a given molecule ID. |

### CHILL / CHILL+

| name | role |
|------|------|
| `BondClassifier` | Bond-classification rule set (staggered / eclipsed windows). |
| `chillRule` | The CHILL water rule set. |
| `chillPlusRule` | The CHILL+ water rule set. |
| `bondClassifier` | Look up a registered bond-classification rule set by name. |
| `registerBondClassifier` | Register (or replace) a named bond-classification rule set. |
| `bondClassifierNames` | Names of every registered bond-classification rule set. |
| `classifyBonds` | Compute and classify bond correlations under an arbitrary rule set. |
| `getCorrelPlus` | Compute CHILL+ bond-order correlations and classify bond types. |
| `getIceTypePlusNoPrint` | Classify each atom's ice type using CHILL+. Does not write a file. |
| `getIceTypePlus` | Classify each atom's ice type using CHILL+ and write to file. |
| `getCorrel` | Compute CHILL bond-order correlations and classify bond types. |
| `getIceTypeNoPrint` | Classify each atom's ice type using CHILL. Does not write a file. |
| `getIceType` | Classify each atom's ice type using CHILL and write to file. |
| `getq6` | Compute the q6 bond order parameter for all atoms. |
| `reclassifyWater` | Reclassify water molecules using averaged q6 and q3 parameters. |
| `printIceType` | Print the ice type classification for the current frame. |

### Descriptors

| name | role |
|------|------|
| `steinhardtQl` | Local and neighbour-averaged Steinhardt parameters of degree `orderL`. |
| `steinhardtQlVoronoi` | Voronoi facet-area weighted Steinhardt parameters. |
| `classifyTemplates` | IRA/Horn overlay onto FCC, HCP, BCC, and SC neighbour shells. |
| `soapSpectrum` | SOAP power spectrum of one particle. |
| `soapSpectrumAll` | SOAP power spectrum of every particle. |
| `voronoiFeature` | Per-atom `[q4, q6, q8]` from the Voronoi-weighted Steinhardt path. |
| `voronoiFeatures` | `[q4, q6, q8]` for every particle from one Voronoi pass per order. |
| `voronoiFacetWeights` | Voronoi facet neighbours and area weights for every particle. |
| `LinearClassifier` | Linear classifier used by `Frame.fit_classifier`. |
| `ira_available` | True when this build linked libira (IRA/SOFI). |
| `ira_match` | IRA overlay of two `n x 3` point sets. Linked when `SEAMS_HAS_IRA`. |
| `sofi_point_group` | SOFI point group of an `n x 3` cloud. Linked when `SEAMS_HAS_IRA`. |
| `lookupTableQ4Vec` | Lookup table for Q4 (`m=0` to `m=8`). |
| `lookupTableQ4` | Lookup table for Q4 at a single `m` (`m=0` to `m=8`). |
| `lookupTableQ8Vec` | Lookup table for Q8 (`m=0` to `m=16`). |
| `lookupTableQ8` | Lookup table for Q8 at a single `m` (`m=0` to `m=16`). |

### Clustering and RDF

| name | role |
|------|------|
| `clusterAnalysis` | Cluster ice-like particles and return the largest ice cluster. |
| `recenterClusterCloud` | Recenter a cluster point cloud for visualization. |
| `rdf2Danalysis_AA` | 2D radial distribution function for identical atom types. |

### Types

| name | role |
|------|------|
| `PointCloudDouble` | Collection of points for a single frame, with box dimensions. |
| `PointDouble` | Per-particle data: coordinates, type, molecule ID, ice classification. |
| `SteinhardtQl` | Per-particle Steinhardt `ql` and neighbour-averaged `qlBar`. |
| `AtomStateType` | Per-atom ice phase classification from CHILL / CHILL+ / q6. |
| `BondType` | Bond classification: staggered, eclipsed, or `out_of_range`. |
| `Result` | Bond correlation result: `classifier` (bond type) and `c_value`. |
| `CrystalKind` | Crystal template kind: `other`, `sc`, `fcc`, `hcp`, `bcc`. |
| `TemplateHit` | IRA/Horn overlay hit: `kind`, `rmsd`, `name`. |
| `VoronoiWeights` | Facet-sharing neighbours and facet-area weights of one particle. |
