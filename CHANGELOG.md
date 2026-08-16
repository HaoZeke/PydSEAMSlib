# Changelog

## 2.2.4

`subprojects/seams-core.wrap` is `68367c0` (linked-cell k-nearest).
`kNearestNeighbourList` keeps the same Python signature.

## 2.2.3

Docs are orgmode plus Shibuya. Autodoc covers `Frame` and `yoda`.

## 2.2.2

The compiled extension is `pydseams.yoda`. `_core` and `cyoda` remain
aliases of that module.

## 2.2.1

Flake-based Nix package for `pydseams`.

## 2.2.0

The import is `pydseams`. `pydseamslib` remains a compatibility alias.
This matches `dseams` (Lua) and the `seams` engine CLI.

## 2.1.0

Python helpers sit on `_core` the way metatomic sits on its C surface.
`ds.read` dispatches by suffix (LAMMPS, XYZ, chemfiles PDB/GRO/DCD,
readcon `.con`). `from_chemfiles`, `from_con`, `from_xyz`, and
`to_solvis` (`pydseams[solvis]`) are first-class.

## 2.0.1

- README documents `pip install` and `frame.to_ase()`.
- `to_ase()` writes `hc` / `ddc` from the last `cages()` result.
- `Frame()` defaults match `read()` (`atom_type` guessed, `bonded="auto"`).
- Sphinx release is 2.0.0. GSoC `pdm.lock` / `package.json` / pybind11 wrap
  are gone.

## 2.0.0

nanobind rewrite against `seams-core` as a library wrap. Public surface
is `Frame` / `read` / `from_ase`. Wheels are CPython 3.12 limited ABI
(`abi3`). Primary author: Ruhila S.

The Lua and Fennel CLI is [yodaStruct](https://github.com/d-SEAMS/yodaStruct).
