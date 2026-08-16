"""Twelve-factor runtime knobs shared with the C++ engine.

Defaults live here. ``SEAMS_CONFIG`` or ``./seams.env`` fills unset
variables. The process environment wins over the file. Function
arguments win over the environment.
"""

from __future__ import annotations

import os
from pathlib import Path

_APPLIED = False


def _strip(line: str) -> str:
    line = line.split("#", 1)[0].strip()
    if (len(line) >= 2) and line[0] == line[-1] and line[0] in {'"', "'"}:
        return line[1:-1]
    return line


def apply_file(path: str | os.PathLike[str], required: bool = True) -> None:
    p = Path(path)
    if not p.is_file():
        if required:
            raise FileNotFoundError(f"SEAMS_CONFIG file not found: {p}")
        return
    for raw in p.read_text().splitlines():
        line = _strip(raw)
        if not line:
            continue
        if line.startswith("export "):
            line = _strip(line[7:])
        if "=" not in line:
            raise ValueError(f"{p}: expected KEY=VAL")
        key, val = line.split("=", 1)
        key = key.strip()
        val = _strip(val)
        os.environ.setdefault(key, val)


def apply() -> None:
    """Load the backing file once. Already-set env vars stay put."""
    global _APPLIED
    if _APPLIED:
        return
    _APPLIED = True
    explicit = os.environ.get("SEAMS_CONFIG")
    if explicit:
        apply_file(explicit, required=True)
    elif Path("seams.env").is_file():
        apply_file("seams.env", required=True)


def reset() -> None:
    """Test helper: allow apply() to run again."""
    global _APPLIED
    _APPLIED = False


def _get(name: str) -> str | None:
    apply()
    val = os.environ.get(name)
    if val is None or val == "":
        return None
    return val


def get_int(name: str, default: int) -> int:
    val = _get(name)
    return default if val is None else int(val)


def get_float(name: str, default: float) -> float:
    val = _get(name)
    return default if val is None else float(val)


def frame(default: int = 1) -> int:
    return get_int("SEAMS_FRAME", default)


def cutoff(default: float = 3.5) -> float:
    return get_float("SEAMS_CUTOFF", default)


def k_neighbors(default: int = 4) -> int:
    return get_int("SEAMS_K", default)


def graph(default: str = "seeded") -> str:
    val = _get("SEAMS_GRAPH")
    return default if val is None else val
