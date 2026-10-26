import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def disable_external_services(monkeypatch):
    """Keep unit tests deterministic even when a developer has a local .env."""
    monkeypatch.setattr(settings, "openai_api_key", None)
    monkeypatch.setattr(settings, "phoenix_collector_endpoint", None)
