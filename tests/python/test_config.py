"""Twelve-factor knobs: file, then env, then the call."""

from pydseams import config


def test_cutoff_defaults(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SEAMS_CUTOFF", raising=False)
    monkeypatch.delenv("SEAMS_CONFIG", raising=False)
    config.reset()
    assert config.cutoff() == 3.5


def test_env_wins_over_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    envfile = tmp_path / "seams.env"
    envfile.write_text("SEAMS_CUTOFF=4.1\nSEAMS_K=8\n")
    monkeypatch.delenv("SEAMS_CUTOFF", raising=False)
    monkeypatch.setenv("SEAMS_K", "16")
    monkeypatch.delenv("SEAMS_CONFIG", raising=False)
    config.reset()
    assert config.cutoff() == 4.1
    assert config.k_neighbors() == 16


def test_explicit_config_path(monkeypatch, tmp_path):
    other = tmp_path / "other.env"
    other.write_text("SEAMS_FRAME=7\n")
    monkeypatch.setenv("SEAMS_CONFIG", str(other))
    monkeypatch.delenv("SEAMS_FRAME", raising=False)
    config.reset()
    assert config.frame() == 7
