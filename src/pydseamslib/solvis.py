"""Optional solvis (PyVista) view of a Frame.

solvis takes an ASE Atoms. This helper is the same pattern as
metatomic's ASE adapter: the C++ core does not know about the viewer.
"""

from __future__ import annotations


def _require_solvis():
    try:
        from solvis.system import System
    except ImportError as exc:
        raise ImportError(
            "solvis interop needs solvis-tools. "
            "Install it with: pip install 'pydseamslib[solvis]'"
        ) from exc
    return System


def to_solvis(frame, expand_box=True):
    """solvis.System wrapping this frame's ASE Atoms."""
    System = _require_solvis()
    return System(frame.to_ase(), expand_box=expand_box)
