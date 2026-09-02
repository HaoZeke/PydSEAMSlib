===================================
Features for kinetic models and ions
===================================

Problem
-------

You have a nucleation trajectory and want one feature vector per frame
for a Markov state model or a committor fit, one integer state per
molecule per frame, and, when the system holds ions, what each ion sees.

Per-frame features
------------------

.. code:: python

    from pydseams import Trajectory
    from pydseams.features import IceFeaturizer

    traj = Trajectory("nucleation.lammpstrj", frame=1, atom_type=2, cutoff=3.5)
    feat = IceFeaturizer(traj, ring_adjacent=True)
    X, S = feat.transform()          # X: (n_frames, 15), S: (n_frames, n_molecules)
    print(feat.feature_names)

``X`` holds cage counts (``n_ice``, ``n_ic``, ``n_ih``, ``n_mixed``), the
largest connected cage cluster ``n_max`` and the cluster count, the
cubicity, the CHILL+ counts on the cutoff graph, the largest CHILL+ bulk
cluster and the six-ring count. ``S`` holds ``STATE_WATER``,
``STATE_IC``, ``STATE_IH`` or ``STATE_MIXED`` per molecule. Both are
plain NumPy arrays and both are deterministic: a feature file from one
machine equals the same file from another to the last integer.

deeptime
--------

.. code:: python

    from pydseams.features import discretize_nmax, to_deeptime

    dtrajs = discretize_nmax(X[:, 1], edges=[10, 50, 150, 400])
    msm = to_deeptime(X, lagtime=5)

``discretize_nmax`` bins the largest-cluster series into integer states
for ``deeptime.markov.msm.MaximumLikelihoodMSM``; ``to_deeptime`` fits a
TICA on the full vector and returns the estimator.

PyEMMA
------

.. code:: python

    from pydseams.features import to_pyemma_featurizer

    featurizer = to_pyemma_featurizer(feat, topology="nucleation.pdb")

The per-frame vector is registered as a custom feature. PyEMMA has been
in maintenance mode since 2022; deeptime is its successor.

Ions
----

Ions are not part of the hydrogen-bond network. The cage assignment runs
on the water and the ions are read against it: build the frame with
every species in the cloud and name the ion types.

.. code:: python

    from pydseams import Trajectory
    from pydseams.features import ION_ICE, IceFeaturizer, ion_environment

    traj = Trajectory("brine.lammpstrj", frame=1, atom_type=1, all_atoms=True)
    feat = IceFeaturizer(traj, ion_types=(3, 4))     # Na, Cl
    x, states = feat.frame_features()
    ions, shell, fraction, ion_states = ion_environment(traj, states, (3, 4))
    trapped = ions[ion_states == ION_ICE]

``ion_environment`` returns, per ion, the water count in its first
shell (within ``cutoff``), the fraction of that shell carrying an ice
label, and a class: ``ION_ICE`` when the whole shell is ice,
``ION_LIQUID`` when none of it is, ``ION_FRONT`` otherwise. With
``ion_types`` set the feature vector gains ``n_ion_ice``,
``n_ion_front``, ``n_ion_liquid`` and the mean shell ice fraction.
