"""ASE ``Atoms`` in and out of a :class:`~pydseams.frame.Frame`.

Optional extra: ``pip install 'pydseamslib[ase]'``. The compiled engine
does not import ASE; this module is the adapter.
"""

from __future__ import annotations


def _require_ase():
    try:
        import ase
        from ase import Atoms
        from ase.data import chemical_symbols
    except ImportError as exc:
        raise ImportError(
            "ASE interop needs the ase package. "
            "Install it with: pip install 'pydseamslib[ase]'"
        ) from exc
    return ase, Atoms, chemical_symbols


def _mask(atoms, select):
    if select is None:
        return [True] * len(atoms)
    if isinstance(select, str):
        return [sym == select for sym in atoms.get_chemical_symbols()]
    number = int(select)
    return [int(z) == number for z in atoms.numbers]


def _restricted_cell(atoms):
    """Canonicalize an ASE cell to LAMMPS restricted-triclinic form."""
    import numpy as np

    if not bool(np.all(atoms.get_pbc())):
        raise ValueError("from_ase requires a cell periodic in all three directions")
    cell = atoms.get_cell()
    matrix = np.asarray(cell, dtype=float)
    scale = max(1.0, float(np.linalg.norm(matrix)))
    if abs(float(np.linalg.det(matrix))) <= np.finfo(float).eps * scale**3:
        raise ValueError("from_ase cannot convert a singular cell")
    restricted, rotation = cell.standard_form("lower")
    restricted = np.asarray(restricted, dtype=float)
    rotation = np.asarray(rotation, dtype=float)
    if np.any(np.diag(restricted) < 0.0):
        restricted = -restricted
        rotation = -rotation
    positions = np.asarray(atoms.get_positions(), dtype=float) @ rotation.T
    origin = np.asarray(atoms.get_celldisp(), dtype=float).reshape(3) @ rotation.T
    return restricted, rotation, positions, origin


def _dump_box(cell, origin):
    """Encode restricted cell rows as LAMMPS bound spans and tilts."""
    lx = float(cell[0, 0])
    xy, ly = float(cell[1, 0]), float(cell[1, 1])
    xz, yz, lz = float(cell[2, 0]), float(cell[2, 1]), float(cell[2, 2])
    xmin = min(0.0, xy, xz, xy + xz)
    xmax = max(0.0, xy, xz, xy + xz)
    ymin = min(0.0, yz)
    ymax = max(0.0, yz)
    box = [lx + xmax - xmin, ly + ymax - ymin, lz, xy, xz, yz]
    box_low = [
        float(origin[0]) + xmin,
        float(origin[1]) + ymin,
        float(origin[2]),
    ]
    return box, box_low


def frame_from_ase(cls, atoms, select="O", cutoff=3.5, bonded="auto"):
    """Construct ``cls`` (a :class:`~pydseams.frame.Frame`) from ASE ``Atoms``.

    Parameters
    ----------
    cls : type
        :class:`~pydseams.frame.Frame` or a subclass.
    atoms : ase.Atoms
        Configuration with a nonsingular cell periodic in all three directions.
    select : str or int, optional
        Chemical symbol or atomic number kept for analysis. Default
        ``"O"``. ``None`` keeps every atom.
    cutoff : float, optional
        Neighbour cutoff in Angstroms. Default ``3.5``.
    bonded : {"auto", "hbond", "cutoff"}, optional
        Graph for rings. ``"auto"`` becomes ``"hbond"`` when the
        ``Atoms`` contain hydrogen, otherwise ``"cutoff"``.

    Returns
    -------
    Frame
        Selected-species cloud plus an optional hydrogen cloud for
        hydrogen-bond analysis.

    Raises
    ------
    ImportError
        If ASE is not installed.
    TypeError
        If ``atoms`` has no ``get_positions``.
    ValueError
        If the cell is singular, is not fully periodic, or ``select`` matches
        no atom.

    Notes
    -----
    Hydrogens stay in a side cloud so the analysed species remain the
    CHILL / ring particles. General cells are rotated into LAMMPS restricted
    form for analysis and restored by :func:`frame_to_ase`.
    """
    _, Atoms, _ = _require_ase()
    if not hasattr(atoms, "get_positions"):
        raise TypeError("from_ase expects an ASE Atoms object")
    keep = _mask(atoms, select)
    if not any(keep):
        raise ValueError(
            f"no atoms matched select={select!r}; "
            f"symbols={sorted(set(atoms.get_chemical_symbols()))}"
        )
    cell, rotation, transformed, origin = _restricted_cell(atoms)
    box, box_low = _dump_box(cell, origin)
    selected_indices = [i for i, yes in enumerate(keep) if yes]
    positions = [xyz for xyz, yes in zip(transformed, keep) if yes]
    numbers = [int(z) for z, yes in zip(atoms.numbers, keep) if yes]
    symbols = [s for s, yes in zip(atoms.get_chemical_symbols(), keep) if yes]
    from .frame import _cloud_from_positions

    source_mol_ids = atoms.get_array("mol-id") if atoms.has("mol-id") else None
    if source_mol_ids is None:
        mol_ids = list(range(1, len(selected_indices) + 1))
    else:
        mol_ids = [int(source_mol_ids[i]) for i in selected_indices]
    cloud = _cloud_from_positions(
        positions,
        box,
        numbers,
        box_low=box_low,
        mol_ids=mol_ids,
    )
    h_indices = [
        i for i, symbol in enumerate(atoms.get_chemical_symbols()) if symbol == "H"
    ]
    h_pos = [transformed[i] for i in h_indices]
    h_cloud = None
    if h_pos:
        if source_mol_ids is None:
            h_mol_ids = []
            for h_index in h_indices:
                distances = atoms.get_distances(h_index, selected_indices, mic=True)
                nearest = min(
                    range(len(selected_indices)), key=distances.__getitem__
                )
                h_mol_ids.append(mol_ids[nearest])
        else:
            h_mol_ids = [int(source_mol_ids[i]) for i in h_indices]
        h_cloud = _cloud_from_positions(
            h_pos,
            box,
            [1] * len(h_pos),
            box_low=box_low,
            mol_ids=h_mol_ids,
        )
    if bonded == "auto":
        bonded = "hbond" if h_cloud is not None else "cutoff"
    return cls(
        atom_type=int(numbers[0]),
        cutoff=cutoff,
        bonded=bonded,
        cloud=cloud,
        h_cloud=h_cloud,
        symbols=symbols,
        cell_rotation=rotation,
    )


def frame_to_ase(frame):
    """Build an ASE ``Atoms`` from a :class:`~pydseams.frame.Frame`.

    Parameters
    ----------
    frame : Frame
        Configuration to export.

    Returns
    -------
    ase.Atoms
        Periodic cell in its imported orientation. Symbols come from the ASE
        import when present; LAMMPS-only frames fall back to ``O``.

    Notes
    -----
    After :meth:`~pydseams.frame.Frame.chill_plus` (or
    :meth:`~pydseams.frame.Frame.chill`), ``atoms.arrays['ice_type']``
    holds the per-atom labels. After
    :meth:`~pydseams.frame.Frame.cages`, ``atoms.arrays['hc']`` and
    ``atoms.arrays['ddc']`` hold the cage flags.
    ``atoms.info['dseams_n_atoms']`` is the analysed particle count.
    """
    import numpy as np

    _, Atoms, _ = _require_ase()
    from .frame import _dump_geometry

    n = frame.n_atoms
    if frame._symbols is not None:
        symbols = list(frame._symbols)
    else:
        # LAMMPS type 8 is oxygen in the periodic table; type 1 or 2
        # from a water dump is not. Prefer O for the analysed species.
        fallback = "O"
        symbols = [fallback] * n
    restricted, origin = _dump_geometry(frame.cloud.box, frame.cloud.boxLow)
    rotation = getattr(frame, "_cell_rotation", None)
    if rotation is None:
        rotation = np.eye(3)
    rotation = np.asarray(rotation, dtype=float)
    positions = np.asarray(frame.positions, dtype=float) @ rotation
    cell = np.asarray(restricted, dtype=float) @ rotation
    celldisp = np.asarray(origin, dtype=float) @ rotation
    atoms = Atoms(
        symbols=symbols,
        positions=positions,
        cell=cell,
        pbc=True,
    )
    atoms.set_celldisp(celldisp)
    ice = [pt.iceType.name for pt in frame.cloud.pts]
    if any(name != "unclassified" for name in ice):
        atoms.arrays["ice_type"] = ice
    score = getattr(frame, "_cages", None)
    if score is not None:
        atoms.arrays["hc"] = list(score.hc)
        atoms.arrays["ddc"] = list(score.ddc)
    atoms.info["dseams_n_atoms"] = n
    return atoms
