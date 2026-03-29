"""Tests for campaign REST endpoints."""

import pytest
from fastapi.testclient import TestClient

from dnd_dm_agent.server import app

client = TestClient(app)


@pytest.fixture
def instance_dir(tmp_path, monkeypatch):
    """Patch PROJECT_ROOT so endpoints use a temp campaigns dir."""
    import dnd_dm_agent.server as srv

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    inst = tmp_path / "campaigns" / "a_most_potent_brew_thork_adventure"
    (inst / "characters").mkdir(parents=True)
    (inst / "campaign_progress.md").write_text(
        "# A Most Potent Brew - thork_adventure\n\n"
        "**Instance:** thork_adventure\n"
        "**Template:** a_most_potent_brew\n"
        "**Created:** 2026-03-28\n\n"
        "## Current Progress\n"
        "- **Act:** Act 1 - The Brewery Investigation\n"
        "- **Beat:** Beat 1.2: Into the Cellar\n\n"
        "## Party\n"
        "- **Thork Ironforge** (Mountain Dwarf Fighter 1) - HP: 10/12\n\n"
        "## Key Decisions\n"
    )
    return tmp_path


def test_list_campaigns_enriched(instance_dir):
    resp = client.get("/api/campaigns")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["instances"]) == 1
    inst = data["instances"][0]
    assert inst["name"] == "a_most_potent_brew_thork_adventure"
    assert inst["display_name"] == "A Most Potent Brew — Thork Adventure"
    assert inst["character"] == "Thork Ironforge · Mountain Dwarf Fighter 1"
    assert inst["beat"] == "Act 1 · Beat 1.2: Into the Cellar"


def test_list_campaigns_empty(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    resp = client.get("/api/campaigns")
    assert resp.status_code == 200
    assert resp.json() == {"instances": []}
