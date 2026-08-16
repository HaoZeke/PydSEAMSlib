"""Optional solvis (PyVista) view of a :class:`~pydseams.frame.Frame`.

solvis takes an ASE ``Atoms``. This helper is the same pattern as
metatomic's ASE adapter: the C++ core does not know about the viewer.
Install with ``pip install 'pydseams[solvis]'``.
"""

from __future__ import annotations


def _require_solvis():
    try:
        from solvis.system import System
    except ImportError as exc:
        raise ImportError(
            "solvis interop needs solvis-tools. "
            "Install it with: pip install 'pydseams[solvis]'"
        ) from exc
    return System


def to_solvis(frame, expand_box=True):
    """Wrap a :class:`~pydseams.frame.Frame` as a ``solvis.System``.

    Parameters
    ----------
    frame : Frame
        Configuration to view. Converted through
        :meth:`~pydseams.frame.Frame.to_ase`.
    expand_box : bool, optional
        Passed to ``solvis.system.System``. Default ``True``.

    Returns
    -------
    solvis.system.System

    Raises
    ------
    ImportError
        If solvis is not installed (``pip install 'pydseams[solvis]'``).
    """
    System = _require_solvis()
    return System(frame.to_ase(), expand_box=expand_box)
