from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def example_traj():
    return Path(__file__).resolve().parent / "data" / "exampleTraj.lammpstrj"
