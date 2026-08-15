# Changelog

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
