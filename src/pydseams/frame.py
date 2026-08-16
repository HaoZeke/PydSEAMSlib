"""User-facing one-frame handle.

Load a LAMMPS dump, an ASE ``Atoms``, or raw arrays, then call
:meth:`Frame.chill_plus` or :meth:`Frame.cages`. Classification does
not write files. Rings use the bonded graph (hydrogen bonds when
hydrogens are available, otherwise the cutoff neighbour list).
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from . import config
from . import yoda


class IceCounts(dict):
    """CHILL / CHILL+ histogram of ice labels on one frame.

    Keys are the ``AtomStateType`` names written by the classifier
    (``cubic``, ``hexagonal``, ``water``, ``interfacial``,
    ``clathrate``, ``interClathrate``, ``unclassified``, ``reCubic``,
    ``reHex``). Missing keys read as ``0`` via attribute access, so
    ``counts.cubic`` and ``counts['cubic']`` are equivalent.

    Notes
    -----
    ``repr`` omits zero-count labels.
    """

    def __missing__(self, key):
        return 0

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return self[name]

    def __repr__(self):
        parts = [f"{k}={v}" for k, v in sorted(self.items()) if v]
        return "IceCounts(" + ", ".join(parts) + ")"


class CageScore:
    """Per-atom hexagonal-cage (HC) and double-diamond-cage (DDC) flags.

    A molecule in an HC is ice Ih; a molecule in a DDC is ice Ic.
    Membership is a boolean per analysed atom.

    Parameters
    ----------
    hc : sequence of bool
        True when the atom belongs to at least one hexagonal cage.
    ddc : sequence of bool
        True when the atom belongs to at least one double-diamond cage.

    Attributes
    ----------
    hc : list of bool
        Per-atom HC membership.
    ddc : list of bool
        Per-atom DDC membership.
    """

    def __init__(self, hc, ddc):
        self.hc = list(hc)
        self.ddc = list(ddc)

    @property
    def n_ih(self):
        """Number of atoms flagged HC (ice Ih)."""
        return sum(1 for flag in self.hc if flag)

    @property
    def n_ic(self):
        """Number of atoms flagged DDC (ice Ic)."""
        return sum(1 for flag in self.ddc if flag)

    @property
    def n_water(self):
        """Number of atoms in neither cage."""
        return sum(1 for h, d in zip(self.hc, self.ddc) if not h and not d)

    def __repr__(self):
        return f"CageScore(n_ih={self.n_ih}, n_ic={self.n_ic}, n_water={self.n_water})"


def _cloud_from_positions(positions, cell, numbers, box_low=None):
    n = len(positions)
    if n == 0:
        raise ValueError("no atoms to load")
    if len(cell) != 3:
        raise ValueError("cell must be three box lengths [lx, ly, lz]")
    cloud = yoda.PointCloudDouble()
    cloud.nop = n
    cloud.currentFrame = 1
    cloud.box = [float(cell[0]), float(cell[1]), float(cell[2])]
    if box_low is None:
        cloud.boxLow = [0.0, 0.0, 0.0]
    else:
        cloud.boxLow = [float(box_low[0]), float(box_low[1]), float(box_low[2])]
    pts = []
    id_map = {}
    for i, xyz in enumerate(positions):
        pt = yoda.PointDouble()
        pt.x = float(xyz[0])
        pt.y = float(xyz[1])
        pt.z = float(xyz[2])
        pt.c_type = int(numbers[i]) if numbers is not None else 1
        pt.atomID = i + 1
        pt.molID = i + 1
        pt.inSlice = True
        pts.append(pt)
        id_map[i + 1] = i
    cloud.pts = pts
    cloud.idIndexMap = id_map
    return cloud


def _guess_lammps_type(filename, frame, region):
    low, high = region if region is not None else ([0, 0, 0], [0, 0, 0])
    sliced = region is not None
    for type_i in (2, 1):
        cloud = yoda.readLammpsTrjreduced(
            filename=filename,
            targetFrame=frame,
            typeI=type_i,
            isSlice=sliced,
            coordLow=list(low),
            coordHigh=list(high),
        )
        if cloud.nop > 0:
            return cloud, type_i
    raise ValueError(f"{filename} frame {frame} has no atoms of type 1 or 2")


class Frame:
    """One configuration: neighbours, rings, CHILL(+), and cage membership.

    Load a LAMMPS dump, an ASE ``Atoms``, or raw arrays, then call
    :meth:`chill_plus` or :meth:`cages`. Classification does not write
    files. Prefer :func:`pydseams.io.read`, :meth:`from_ase`, or
    :meth:`from_arrays` over constructing this class by filename.

    Parameters
    ----------
    filename : path-like, optional
        LAMMPS dump. Types 1 and 2 are treated as hydrogen and oxygen
        unless ``atom_type`` is set.
    frame : int, optional
        1-indexed frame. Default ``1``.
    atom_type : int or None, optional
        Species to analyse. ``None`` picks oxygen (type 2) if that type
        is present, otherwise type 1 (mW-style single-site dumps).
    cutoff : float, optional
        Neighbour cutoff in Angstroms. Default ``3.5``.
    bonded : {"auto", "hbond", "cutoff"}, optional
        Graph for rings. ``"auto"`` uses hydrogen bonds when hydrogens
        are available, otherwise the cutoff neighbour list.
    region : ((xlo, ylo, zlo), (xhi, yhi, zhi)) or None, optional
        Optional rectangular slice passed to
        :func:`pydseams.yoda.readLammpsTrjreduced`.

    Raises
    ------
    ValueError
        If ``bonded`` is not one of ``auto``, ``hbond``, ``cutoff``, or
        if a LAMMPS dump has no atoms of type 1 or 2.
    TypeError
        If neither a filename nor a pre-built cloud is supplied.

    Notes
    -----
    Keyword-only ``cloud``, ``h_cloud``, and ``symbols`` are the
    constructor plumbing used by :meth:`from_ase` and
    :meth:`from_arrays`.
    """

    def __init__(
        self,
        filename=None,
        frame=None,
        atom_type=None,
        cutoff=None,
        bonded="auto",
        region=None,
        *,
        cloud=None,
        h_cloud=None,
        symbols=None,
    ):
        if bonded not in ("hbond", "cutoff", "auto"):
            raise ValueError('bonded must be "hbond", "cutoff", or "auto"')
        if frame is None:
            frame = config.frame()
        if cutoff is None:
            cutoff = config.cutoff()
        self.region = region
        self.filename = str(Path(filename).resolve()) if filename is not None else None
        self.frame = frame
        self.cutoff = cutoff
        self._h_cloud = h_cloud
        self._symbols = symbols
        self._nlist = None
        self._hbonds = None
        self._rings = None
        self._cages = None
        self._classifier = None
        self._ring_updater = yoda.RingUpdater(6)
        self._affiliation_updater = None

        if cloud is not None:
            self.cloud = cloud
            self.atom_type = atom_type
        elif self.filename is not None:
            if atom_type is None:
                self.cloud, self.atom_type = _guess_lammps_type(
                    self.filename, frame, region
                )
            else:
                self.atom_type = atom_type
                self.cloud = self._read(frame)
        else:
            raise TypeError("Frame needs a filename, cloud=, from_ase, or from_arrays")

        if bonded == "auto":
            self.bonded = "hbond" if self._can_hbond() else "cutoff"
        else:
            self.bonded = bonded

    def _can_hbond(self):
        if self._h_cloud is not None:
            return self._h_cloud.nop > 0
        return self.filename is not None and self.atom_type == 2

    def _read(self, frame):
        low, high = self.region if self.region is not None else ([0, 0, 0], [0, 0, 0])
        return yoda.readLammpsTrjreduced(
            filename=self.filename,
            targetFrame=frame,
            typeI=self.atom_type,
            isSlice=self.region is not None,
            coordLow=list(low),
            coordHigh=list(high),
        )

    @classmethod
    def from_file(
        cls, filename, frame=None, atom_type=None, cutoff=None, bonded="auto", region=None
    ):
        """Load a LAMMPS dump through :func:`pydseams.yoda.readLammpsTrjreduced`.

        Parameters
        ----------
        filename : path-like
            LAMMPS dump (``.lammpstrj``, ``.dump``, ``.lammps``).
        frame : int, optional
            1-indexed frame. Default ``1``.
        atom_type : int or None, optional
            Species to keep. ``None`` tries type 2 (oxygen) then type 1.
        cutoff : float, optional
            Neighbour cutoff in Angstroms. Default ``3.5``.
        bonded : {"auto", "hbond", "cutoff"}, optional
            Graph for rings.
        region : ((xlo, ylo, zlo), (xhi, yhi, zhi)) or None, optional
            Optional rectangular slice.

        Returns
        -------
        Frame
        """
        return (
            cls(
                filename,
                frame=frame,
                atom_type=atom_type if atom_type is not None else 2,
                cutoff=cutoff,
                bonded=bonded,
                region=region,
            )
            if atom_type is not None
            else cls._from_file_guess(filename, frame, cutoff, bonded, region)
        )

    @classmethod
    def _from_file_guess(cls, filename, frame, cutoff, bonded, region):
        path = str(Path(filename).resolve())
        cloud, type_i = _guess_lammps_type(path, frame, region)
        return cls(
            filename=path,
            frame=frame,
            atom_type=type_i,
            cutoff=cutoff,
            bonded=bonded,
            region=region,
            cloud=cloud,
        )

    @classmethod
    def from_arrays(
        cls, positions, cell, numbers=None, cutoff=None, bonded="cutoff", box_low=None
    ):
        """Build a frame from ``(N, 3)`` positions and three box lengths.

        Parameters
        ----------
        positions : sequence of (x, y, z)
            Cartesian coordinates.
        cell : sequence of float
            Orthorhombic box lengths ``[lx, ly, lz]``.
        numbers : sequence of int, optional
            Per-atom type codes stored as ``c_type``. Default ``1``.
        cutoff : float, optional
            Neighbour cutoff in Angstroms. Default ``3.5``.
        bonded : {"auto", "hbond", "cutoff"}, optional
            Graph for rings. Default ``"cutoff"``.
        box_low : sequence of float, optional
            Box origin. Default ``(0, 0, 0)``.

        Returns
        -------
        Frame

        Raises
        ------
        ValueError
            If ``positions`` is empty or ``cell`` is not three lengths.
        """
        n = len(positions)
        nums = list(numbers) if numbers is not None else [1] * n
        types = sorted(set(int(x) for x in nums))
        atom_type = types[0] if len(types) == 1 else 1
        cloud = _cloud_from_positions(positions, cell, nums, box_low)
        return cls(
            atom_type=atom_type,
            cutoff=cutoff,
            bonded=bonded,
            cloud=cloud,
        )

    @classmethod
    def from_xyz(cls, filename, cutoff=None, bonded="cutoff", atom_type=None):
        """Load an XYZ file through :func:`pydseams.yoda.readXYZ`.

        Parameters
        ----------
        filename : path-like
            XYZ structure.
        cutoff : float, optional
            Neighbour cutoff in Angstroms. Default ``3.5``.
        bonded : {"auto", "hbond", "cutoff"}, optional
            Graph for rings. Default ``"cutoff"``.
        atom_type : int or None, optional
            Species to analyse. ``None`` uses the first particle's
            ``c_type``.

        Returns
        -------
        Frame

        Raises
        ------
        RuntimeError
            If this build has no ``readXYZ``.
        """
        if not hasattr(yoda, "readXYZ"):
            raise RuntimeError("this build has no readXYZ")
        cloud = yoda.readXYZ(str(filename))
        typ = atom_type
        if typ is None and cloud.nop > 0:
            typ = int(cloud.pts[0].c_type)
        return cls(
            filename=str(Path(filename).resolve()),
            atom_type=typ or 1,
            cutoff=cutoff,
            bonded=bonded,
            cloud=cloud,
        )

    @classmethod
    def from_chemfiles(
        cls,
        filename,
        frame=None,
        type_filter=-1,
        cutoff=None,
        bonded="cutoff",
        atom_type=None,
    ):
        """Load PDB/GRO/DCD (or any chemfiles format) when chemfiles is linked.

        Parameters
        ----------
        filename : path-like
            Trajectory chemfiles can read.
        frame : int, optional
            1-indexed frame. Default ``1``.
        type_filter : int, optional
            Chemfiles type filter. ``-1`` keeps every type.
        cutoff : float, optional
            Neighbour cutoff in Angstroms. Default ``3.5``.
        bonded : {"auto", "hbond", "cutoff"}, optional
            Graph for rings. Default ``"cutoff"``.
        atom_type : int or None, optional
            Species to analyse. ``None`` uses the first particle's
            ``c_type``.

        Returns
        -------
        Frame

        Raises
        ------
        RuntimeError
            If chemfiles is not linked in this build of seams-core.
        """
        if not hasattr(yoda, "readChemfiles"):
            raise RuntimeError("chemfiles is not linked in this build of seams-core")
        if frame is None:
            frame = config.frame()
        cloud = yoda.readChemfiles(str(filename), int(frame), int(type_filter))
        typ = atom_type
        if typ is None and cloud.nop > 0:
            typ = int(cloud.pts[0].c_type)
        return cls(
            filename=str(Path(filename).resolve()),
            frame=frame,
            atom_type=typ or 1,
            cutoff=cutoff,
            bonded=bonded,
            cloud=cloud,
        )

    @classmethod
    def from_con(cls, filename, frame=None, cutoff=None, bonded="cutoff", atom_type=None):
        """Load an eOn ``.con`` file when readcon-core is linked.

        Parameters
        ----------
        filename : path-like
            eOn ``.con`` trajectory.
        frame : int, optional
            1-indexed frame. Default ``1``.
        cutoff : float, optional
            Neighbour cutoff in Angstroms. Default ``3.5``.
        bonded : {"auto", "hbond", "cutoff"}, optional
            Graph for rings. Default ``"cutoff"``.
        atom_type : int or None, optional
            Species to analyse. ``None`` uses the first particle's
            ``c_type``.

        Returns
        -------
        Frame

        Raises
        ------
        RuntimeError
            If readcon-core is not linked in this build of seams-core.
        """
        if not hasattr(yoda, "readCon"):
            raise RuntimeError("readcon-core is not linked in this build of seams-core")
        if frame is None:
            frame = config.frame()
        cloud = yoda.readCon(str(filename), int(frame))
        typ = atom_type
        if typ is None and cloud.nop > 0:
            typ = int(cloud.pts[0].c_type)
        return cls(
            filename=str(Path(filename).resolve()),
            frame=frame,
            atom_type=typ or 1,
            cutoff=cutoff,
            bonded=bonded,
            cloud=cloud,
        )

    @classmethod
    def from_ase(cls, atoms, select="O", cutoff=None, bonded="auto"):
        """Load an ASE ``Atoms``. ``select`` is a symbol, atomic number, or None.

        Parameters
        ----------
        atoms : ase.Atoms
            Configuration with an orthorhombic cell.
        select : str or int, optional
            Chemical symbol or atomic number of the species to analyse.
            Default ``"O"``. ``None`` keeps every atom.
        cutoff : float, optional
            Neighbour cutoff in Angstroms. Default ``3.5``.
        bonded : {"auto", "hbond", "cutoff"}, optional
            Graph for rings. ``"auto"`` uses hydrogen bonds when the
            ``Atoms`` contain H.

        Returns
        -------
        Frame
        """
        from .aseio import frame_from_ase

        return frame_from_ase(cls, atoms, select=select, cutoff=cutoff, bonded=bonded)

    def to_ase(self):
        """ASE ``Atoms`` for this frame.

        Returns
        -------
        ase.Atoms
            Orthorhombic cell, ``pbc=True``. After :meth:`chill_plus`
            (or :meth:`chill`), ``arrays['ice_type']`` holds the labels.
            After :meth:`cages`, ``arrays['hc']`` and ``arrays['ddc']``
            hold the cage flags.
        """
        from .aseio import frame_to_ase

        return frame_to_ase(self)

    def to_solvis(self, expand_box=True):
        """``solvis.System`` for this frame.

        Parameters
        ----------
        expand_box : bool, optional
            Passed to ``solvis.system.System``. Default ``True``.

        Returns
        -------
        solvis.system.System

        Notes
        -----
        Optional extra: ``pip install 'pydseams[solvis]'``.
        """
        from .solvis import to_solvis

        return to_solvis(self, expand_box=expand_box)

    @property
    def n_atoms(self):
        """Number of particles in the analysed cloud (``cloud.nop``)."""
        return self.cloud.nop

    @property
    def box(self):
        """Orthorhombic box lengths ``[lx, ly, lz]``."""
        return list(self.cloud.box)

    @property
    def positions(self):
        """List of ``(x, y, z)`` coordinates for the analysed particles."""
        return [(pt.x, pt.y, pt.z) for pt in self.cloud.pts]

    @property
    def neighbor_list(self):
        """Cutoff neighbour list from :func:`pydseams.yoda.neighListO`.

        Built once per loaded frame and cached. Rows are atom IDs of
        neighbours within :attr:`cutoff` for :attr:`atom_type`.
        """
        if self._nlist is None:
            self._nlist = yoda.neighListO(
                rcutoff=self.cutoff, yCloud=self.cloud, typeI=self.atom_type
            )
        return self._nlist

    @property
    def hbonds(self):
        """Hydrogen-bond neighbour list.

        Uses :func:`pydseams.yoda.populateHbondsWithInputClouds` when
        an ASE hydrogen cloud is attached, otherwise
        :func:`pydseams.yoda.populateHbonds` on the LAMMPS dump.

        Raises
        ------
        ValueError
            If no hydrogens are available (arrays-only frame, or
            ``bonded='hbond'`` without H).
        """
        if self._hbonds is None:
            if self._h_cloud is not None:
                self._hbonds = yoda.populateHbondsWithInputClouds(
                    yCloud=self.cloud,
                    hCloud=self._h_cloud,
                    nList=self.neighbor_list,
                )
            elif self.filename is not None:
                self._hbonds = yoda.populateHbonds(
                    filename=self.filename,
                    yCloud=self.cloud,
                    nList=self.neighbor_list,
                    targetFrame=self.frame,
                    Htype=1,
                )
            else:
                raise ValueError(
                    "Hydrogen-bond analysis needs hydrogens. Pass ASE Atoms "
                    "that include H, a LAMMPS dump with H, or set bonded='cutoff'."
                )
        return self._hbonds

    def load_frame(self, frame):
        """Reload a later (or earlier) frame from the same trajectory file.

        Parameters
        ----------
        frame : int
            1-indexed frame to read.

        Raises
        ------
        ValueError
            If this ``Frame`` was built from arrays or ASE and has no
            trajectory path.

        Notes
        -----
        Clears cached neighbours, hydrogen bonds, rings, and cages.
        """
        if self.filename is None:
            raise ValueError("load_frame needs a trajectory file")
        self.frame = frame
        self.cloud = self._read(frame)
        self._nlist = None
        self._hbonds = None
        self._rings = None
        self._cages = None

    @property
    def bonds_by_index(self):
        """Index-based bonded graph used for rings.

        Hydrogen-bond list when :attr:`bonded` is ``"hbond"``, otherwise
        the cutoff neighbour list. Converted with
        :func:`pydseams.yoda.neighbourListByIndex`.
        """
        source = self.neighbor_list if self.bonded == "cutoff" else self.hbonds
        return yoda.neighbourListByIndex(yCloud=self.cloud, nList=source)

    @property
    def rings(self):
        """Primitive rings up to size 6 on :attr:`bonds_by_index`.

        Computed by :class:`pydseams.yoda.RingUpdater` and cached.
        """
        if self._rings is None:
            self._rings = self._ring_updater.update(self.bonds_by_index)
        return self._rings

    @property
    def rings_recomputed_sources(self):
        """Sources recomputed by the last :class:`~pydseams.yoda.RingUpdater` pass."""
        return self._ring_updater.lastRecomputedSources()

    def _count_ice(self):
        names = [pt.iceType.name for pt in self.cloud.pts]
        return IceCounts(Counter(names))

    def chill_plus(self):
        """CHILL+ labels for every analysed atom. Does not write a file.

        Calls :func:`pydseams.yoda.getCorrelPlus` then
        :func:`pydseams.yoda.getIceTypePlusNoPrint` on
        :attr:`neighbor_list`. Mutates ``cloud.pts[].iceType``.

        Returns
        -------
        IceCounts
            Histogram of CHILL+ labels on this frame.
        """
        yoda.getCorrelPlus(yCloud=self.cloud, nList=self.neighbor_list, isSlice=False)
        yoda.getIceTypePlusNoPrint(
            yCloud=self.cloud, nList=self.neighbor_list, isSlice=False
        )
        return self._count_ice()

    def chill(self):
        """CHILL labels for every analysed atom. Does not write a file.

        Calls :func:`pydseams.yoda.getCorrel` then
        :func:`pydseams.yoda.getIceTypeNoPrint` on
        :attr:`neighbor_list`. Mutates ``cloud.pts[].iceType``.

        Returns
        -------
        IceCounts
            Histogram of CHILL labels on this frame.
        """
        yoda.getCorrel(yCloud=self.cloud, nList=self.neighbor_list, isSlice=False)
        yoda.getIceTypeNoPrint(
            yCloud=self.cloud, nList=self.neighbor_list, isSlice=False
        )
        return self._count_ice()

    def classify_chill_plus(self):
        """Alias of :meth:`chill_plus`."""
        return self.chill_plus()

    def classify_chill(self):
        """Alias of :meth:`chill`."""
        return self.chill()

    def cages(self, seeded=True, k=4, candidate_cutoff=None):
        """Ice score: HC = Ih, DDC = Ic, neither = water.

        Parameters
        ----------
        seeded : bool, optional
            ``True`` (default) is the hysteresis construction: mutual
            four-nearest seeds, union-graph completion
            (:meth:`seeded_affiliation`). ``False`` is cutoff-graph
            affiliation on this frame's six-rings
            (:meth:`cage_affiliation`).
        k : int, optional
            Neighbours kept in the seeded k-nearest graphs. Default
            ``4``.
        candidate_cutoff : float or None, optional
            Candidate-list cutoff for the k-nearest graphs. ``None``
            uses :attr:`cutoff` ``+ 1.5``.

        Returns
        -------
        CageScore
            Per-atom HC/DDC flags. Cached as ``_cages`` for
            :meth:`to_ase`.
        """
        if seeded:
            score = self.seeded_affiliation(k=k, candidate_cutoff=candidate_cutoff)
        else:
            aff = self.cage_affiliation()
            n = self.n_atoms
            hc = [False] * n
            ddc = [False] * n
            for ring, is_hc, is_ddc in zip(aff["six_rings"], aff["hc"], aff["ddc"]):
                for atom in ring:
                    if 0 <= atom < n:
                        hc[atom] = hc[atom] or bool(is_hc)
                        ddc[atom] = ddc[atom] or bool(is_ddc)
            score = CageScore(hc, ddc)
        self._cages = score
        return score

    def cage_affiliation(self):
        """Order-free per-ring HC/DDC flags on this frame's six-rings.

        Uses :class:`pydseams.yoda.AffiliationUpdater` on the
        cutoff-or-hbond six-rings.

        Returns
        -------
        dict
            ``six_rings`` (list of 6-cycles), ``hc`` and ``ddc``
            (per-ring bools), and ``reclassified`` (updater delta).
        """
        six = [r for r in self.rings if len(r) == 6]
        if self._affiliation_updater is None:
            self._affiliation_updater = yoda.AffiliationUpdater()
        hc, ddc = self._affiliation_updater.update(six, self.bonds_by_index)
        return {
            "six_rings": six,
            "hc": list(hc),
            "ddc": list(ddc),
            "reclassified": self._affiliation_updater.lastReclassified(),
        }

    def seeded_affiliation(self, k=4, candidate_cutoff=None):
        """Seeded (hysteresis) per-atom cage flags.

        Strict-graph seeds from a mutual k-nearest list, permissive
        completion on the union k-nearest list. Delegates to
        :func:`pydseams.yoda.seededCageAffiliation`.

        Parameters
        ----------
        k : int, optional
            Neighbours kept in each k-nearest graph. Default ``4``.
        candidate_cutoff : float or None, optional
            Candidate-list cutoff. ``None`` uses :attr:`cutoff`
            ``+ 1.5``.

        Returns
        -------
        CageScore
        """
        cut = self.cutoff + 1.5 if candidate_cutoff is None else candidate_cutoff
        strict = yoda.neighbourListByIndex(
            self.cloud,
            yoda.kNearestNeighbourList(self.cloud, k, cut, self.atom_type, True),
        )
        union = yoda.neighbourListByIndex(
            self.cloud,
            yoda.kNearestNeighbourList(self.cloud, k, cut, self.atom_type, False),
        )
        six_s = [r for r in yoda.ringNetwork(strict, 6) if len(r) == 6]
        six_u = [r for r in yoda.ringNetwork(union, 6) if len(r) == 6]
        hc, ddc = yoda.seededCageAffiliation(six_s, strict, six_u, union)
        return CageScore(hc, ddc)

    def find_prisms(self, output_dir="output/", max_depth=6, shape_matching=False):
        """Identify prism blocks and write engine output under ``output_dir``.

        Parameters
        ----------
        output_dir : path-like, optional
            Directory passed to :func:`pydseams.yoda.prismAnalysis`.
            Default ``"output/"``.
        max_depth : int, optional
            Largest ring size considered. Default ``6``.
        shape_matching : bool, optional
            Enable TUM shape matching inside the prism search.

        Notes
        -----
        This path writes files. :meth:`chill_plus` and :meth:`cages`
        do not.
        """
        hbonds_idx = yoda.neighbourListByIndex(yCloud=self.cloud, nList=self.hbonds)
        yoda.prismAnalysis(
            path=output_dir,
            rings=self.rings,
            nList=hbonds_idx,
            yCloud=self.cloud,
            maxDepth=max_depth,
            atomID=0,
            firstFrame=self.frame,
            currentFrame=self.frame,
            doShapeMatching=shape_matching,
        )

    def monolayer_rings(self, output_dir, sheet_area, max_depth=4):
        """Classify quasi-2D polygon rings and read coverage back.

        Parameters
        ----------
        output_dir : path-like
            Directory for :func:`pydseams.yoda.polygonRingAnalysis`.
        sheet_area : float
            Sheet area passed to the engine.
        max_depth : int, optional
            Largest ring size. Default ``4``.

        Returns
        -------
        dict
            ``{ring_size: {"count": int, "coverage_xy": float}}``
            parsed from ``topoMonolayer/coverageAreaXY.dat``.
        """
        rings = yoda.ringNetwork(self.bonds_by_index, max_depth)
        yoda.polygonRingAnalysis(
            path=str(output_dir) + "/",
            rings=rings,
            nList=self.bonds_by_index,
            yCloud=self.cloud,
            maxDepth=max_depth,
            sheetArea=sheet_area,
            firstFrame=self.frame,
        )
        counts = {}
        cov = (
            (Path(output_dir) / "topoMonolayer" / "coverageAreaXY.dat")
            .read_text()
            .splitlines()
        )
        fields = cov[-1].split()[1:]
        for size, n, area in zip(fields[::3], fields[1::3], fields[2::3]):
            counts[int(size)] = {"count": int(n), "coverage_xy": float(area)}
        return counts

    def rdf_2d(self, output_dir, cutoff=12.0, binwidth=0.05):
        """2D radial distribution function for identical atom types.

        Parameters
        ----------
        output_dir : path-like
            Directory for :func:`pydseams.yoda.rdf2Danalysis_AA`.
        cutoff : float, optional
            RDF cutoff in Angstroms. Default ``12.0``.
        binwidth : float, optional
            Histogram width. Default ``0.05``.

        Returns
        -------
        r, g : list of float
            Bin centres and ``g(r)`` parsed from
            ``topoMonolayer/rdf.dat``.
        """
        yoda.rdf2Danalysis_AA(
            path=str(output_dir) + "/",
            rdfValues=[],
            yCloud=self.cloud,
            cutoff=cutoff,
            binwidth=binwidth,
            firstFrame=self.frame,
            finalFrame=self.frame,
        )
        r, g = [], []
        rdf = (Path(output_dir) / "topoMonolayer" / "rdf.dat").read_text().splitlines()
        for line in rdf:
            parts = line.split()
            if len(parts) == 2:
                r.append(float(parts[0]))
                g.append(float(parts[1]))
        return r, g

    def steinhardt(self, order_l=6):
        """Local and neighbour-averaged Steinhardt parameters.

        Parameters
        ----------
        order_l : int, optional
            Degree ``l`` (3, 4, or 6). Default ``6``.

        Returns
        -------
        dict
            ``ql`` and ``ql_bar`` lists from
            :func:`pydseams.yoda.steinhardtQl`.
        """
        result = yoda.steinhardtQl(
            yCloud=self.cloud, nList=self.neighbor_list, orderL=order_l
        )
        return {"ql": list(result.ql), "ql_bar": list(result.qlBar)}

    def steinhardt_voronoi(self, order_l=6, cutoff=None):
        """Voronoi facet-area weighted Steinhardt parameters.

        Parameters
        ----------
        order_l : int, optional
            Degree ``l``. Default ``6``.
        cutoff : float or None, optional
            Candidate cutoff for the Voronoi pass. ``None`` uses
            :attr:`cutoff`.

        Returns
        -------
        dict
            ``ql`` and ``ql_bar`` lists from
            :func:`pydseams.yoda.steinhardtQlVoronoi`.
        """
        result = yoda.steinhardtQlVoronoi(
            yCloud=self.cloud,
            candidateCutoff=cutoff if cutoff is not None else self.cutoff,
            orderL=order_l,
        )
        return {"ql": list(result.ql), "ql_bar": list(result.qlBar)}

    def classify_templates(self, k_neigh=12):
        """IRA/Horn overlay onto FCC, HCP, BCC, and SC neighbour shells.

        Parameters
        ----------
        k_neigh : int, optional
            Neighbours in each template shell. Default ``12``.

        Returns
        -------
        list of dict
            Each hit has ``name``, ``rmsd``, and ``kind``.
        """
        hits = yoda.classifyTemplates(self.cloud, self.neighbor_list, k_neigh)
        rows = []
        for h in hits:
            name = h.name
            kind = name or getattr(h.kind, "name", str(h.kind))
            rows.append({"name": name, "rmsd": h.rmsd, "kind": kind})
        return rows

    def soap(self, iatom=None, n_max=3, l_max=6, rcut=None):
        """SOAP power spectrum of one particle, or of every particle.

        Parameters
        ----------
        iatom : int or None, optional
            Particle index. ``None`` (default) computes every particle
            via :func:`pydseams.yoda.soapSpectrumAll`.
        n_max : int, optional
            Radial basis size. Default ``3``.
        l_max : int, optional
            Angular momentum cutoff. Default ``6``.
        rcut : float or None, optional
            SOAP cutoff. ``None`` uses :attr:`cutoff`.

        Returns
        -------
        list of float or list of list of float
            One spectrum, or one spectrum per particle.
        """
        r = self.cutoff if rcut is None else rcut
        if iatom is None:
            return [
                list(spec)
                for spec in yoda.soapSpectrumAll(
                    self.cloud, self.neighbor_list, n_max, l_max, r
                )
            ]
        return list(
            yoda.soapSpectrum(self.cloud, iatom, self.neighbor_list, n_max, l_max, r)
        )

    def voronoi_features(self, cutoff=None):
        """Per-atom ``[q4, q6, q8]`` from one Voronoi-weighted pass.

        Parameters
        ----------
        cutoff : float or None, optional
            Candidate cutoff. ``None`` uses :attr:`cutoff`.

        Returns
        -------
        list of list of float
            One ``[q4, q6, q8]`` row per particle from
            :func:`pydseams.yoda.voronoiFeatures`.
        """
        cut = self.cutoff if cutoff is None else cutoff
        return [list(row) for row in yoda.voronoiFeatures(self.cloud, cut)]

    def fit_classifier(self, X, y, labels=None):
        """Fit a :class:`pydseams.yoda.LinearClassifier` on feature rows.

        Parameters
        ----------
        X : sequence of sequence of float
            Feature matrix.
        y : sequence of int
            Integer class labels.
        labels : sequence of str, optional
            Human-readable class names stored on the classifier.

        Returns
        -------
        pydseams.yoda.LinearClassifier
            Fitted classifier, also stored on the frame.
        """
        clf = yoda.LinearClassifier()
        if labels is not None:
            clf.labels = list(labels)
        clf.fit(X, y)
        self._classifier = clf
        return clf

    def predict_class(self, x):
        """Predict a class for one feature row.

        Parameters
        ----------
        x : sequence of float
            Feature vector matching the last :meth:`fit_classifier`
            fit.

        Returns
        -------
        int
            Predicted class index.

        Raises
        ------
        RuntimeError
            If :meth:`fit_classifier` has not been called.
        """
        if self._classifier is None:
            raise RuntimeError("fit_classifier must be called first")
        return self._classifier.predict(x)


def read(filename, **kwargs):
    """Load a trajectory. Format follows the suffix.

    Thin wrapper around :func:`pydseams.io.read`.

    Parameters
    ----------
    filename : path-like
        Trajectory or structure file.
    **kwargs
        Forwarded to :func:`pydseams.io.read` (``frame``, ``cutoff``,
        ``bonded``, ``atom_type``, ``region``, ...).

    Returns
    -------
    Frame
    """
    from .io import read as _read

    return _read(filename, **kwargs)
