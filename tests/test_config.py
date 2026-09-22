"""Settings behaviour that the rest of the app relies on."""

import pytest

from app.config import Settings


def test_storage_directories_are_derived_from_storage_path(tmp_path):
    settings = Settings(STORAGE_PATH=str(tmp_path))
    assert settings.papers_dir == tmp_path / "papers"
    assert settings.content_dir == tmp_path / "content"


def test_missing_coze_key_warns_but_stays_usable(monkeypatch):
    monkeypatch.delenv("COZE_API_KEY", raising=False)
    with pytest.warns(UserWarning, match="COZE_API_KEY"):
        settings = Settings(_env_file=None, COZE_API_KEY="")
    assert settings.COZE_API_KEY == ""


def test_configured_coze_key_does_not_warn():
    settings = Settings(_env_file=None, COZE_API_KEY="pat-test")
    assert settings.COZE_API_KEY == "pat-test"


def test_environment_overrides_defaults(monkeypatch):
    monkeypatch.setenv("APP_PORT", "9000")
    monkeypatch.setenv("CRAWL_MAX_PAPERS_PER_SOURCE", "7")
    settings = Settings(_env_file=None)
    assert settings.APP_PORT == 9000
    assert settings.CRAWL_MAX_PAPERS_PER_SOURCE == 7
