"""Tests for campaign REST endpoints."""

import json as json_lib

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
    (inst / "characters" / "thork.md").write_text("# Thork")
    (inst / "campaign_progress.md").write_text(
        "# A Most Potent Brew - thork_adventure\n\n"
        "**Instance:** thork_adventure\n"
        "**Template:** a_most_potent_brew\n"
        "**Created:** 2026-03-28\n\n"
        "## Current Progress\n"
        "- **Act:** Act 1 - The Brewery Investigation\n"
        "- **Beat:** Beat 1.2 - Into the Cellar\n\n"
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
    assert inst["character_file"] == "thork"
    assert inst["beat"] == "Act 1 · Beat 1.2 - Into the Cellar"


def test_list_campaigns_empty(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    resp = client.get("/api/campaigns")
    assert resp.status_code == 200
    assert resp.json() == {"instances": []}


@pytest.fixture
def templates_dir(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    pregen = tmp_path / "available_campaigns" / "a_most_potent_brew" / "pregenerated_characters"
    pregen.mkdir(parents=True)
    (pregen / "dwarf_fighter.md").write_text("# Dwarf Fighter")
    (pregen / "elf_wizard.md").write_text("# Elf Wizard")
    return tmp_path


def test_list_templates(templates_dir):
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["templates"]) == 1
    t = data["templates"][0]
    assert t["name"] == "a_most_potent_brew"
    assert t["display_name"] == "A Most Potent Brew"
    char_names = [c["name"] for c in t["characters"]]
    assert "dwarf_fighter" in char_names
    assert "elf_wizard" in char_names


def test_list_templates_empty(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    assert resp.json() == {"templates": []}


@pytest.fixture
def create_env(tmp_path, monkeypatch):
    """Temp dir with one template and one pregenerated character."""
    import dnd_dm_agent.server as srv
    import dnd_dm_agent.tools.campaign_instance_tools as cit

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(cit, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(cit, "CAMPAIGNS_DIR", tmp_path / "campaigns")
    pregen = tmp_path / "available_campaigns" / "a_most_potent_brew" / "pregenerated_characters"
    pregen.mkdir(parents=True)
    (pregen / "dwarf_fighter.md").write_text("# Dwarf Fighter\nHP: 12/12")
    return tmp_path


def test_create_campaign(create_env):
    resp = client.post("/api/campaigns", json={"template": "a_most_potent_brew", "character": "dwarf_fighter"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["instance"] == "a_most_potent_brew_dwarf_fighter"
    assert data["character"] == "dwarf_fighter"
    char_file = create_env / "campaigns" / "a_most_potent_brew_dwarf_fighter" / "characters" / "dwarf_fighter.md"
    assert char_file.exists()
    assert "HP: 12/12" in char_file.read_text()


def test_create_campaign_duplicate(create_env):
    client.post("/api/campaigns", json={"template": "a_most_potent_brew", "character": "dwarf_fighter"})
    resp = client.post("/api/campaigns", json={"template": "a_most_potent_brew", "character": "dwarf_fighter"})
    assert resp.status_code == 409


def test_create_campaign_bad_template(create_env):
    resp = client.post("/api/campaigns", json={"template": "nonexistent", "character": "dwarf_fighter"})
    assert resp.status_code == 400


@pytest.fixture
def deletable_instance(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    inst = tmp_path / "campaigns" / "a_most_potent_brew_thork_adventure"
    (inst / "characters").mkdir(parents=True)
    (inst / "campaign_progress.md").write_text("# test")
    return tmp_path


def test_delete_campaign(deletable_instance):
    resp = client.delete("/api/campaigns/a_most_potent_brew_thork_adventure")
    assert resp.status_code == 204
    assert not (deletable_instance / "campaigns" / "a_most_potent_brew_thork_adventure").exists()


def test_delete_campaign_not_found(deletable_instance):
    resp = client.delete("/api/campaigns/nonexistent_campaign")
    assert resp.status_code == 404


def test_delete_campaign_path_traversal(deletable_instance):
    resp = client.delete("/api/campaigns/..%2Fsomething")
    assert resp.status_code in (400, 404)


@pytest.fixture
def map_env(tmp_path, monkeypatch):
    """Instance with campaign_progress.md containing a Template field."""
    import dnd_dm_agent.server as srv

    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    inst = tmp_path / "campaigns" / "a_most_potent_brew_thork_adventure"
    inst.mkdir(parents=True)
    (inst / "campaign_progress.md").write_text("**Template:** a_most_potent_brew\n**Instance:** thork_adventure\n")
    return tmp_path


def test_get_map_no_map_state(map_env):
    resp = client.get("/api/map/a_most_potent_brew_thork_adventure")
    assert resp.status_code == 200
    assert resp.json() == {"mode": None}


def test_get_map_dynamic_only_when_no_static(map_env):
    inst = map_env / "campaigns" / "a_most_potent_brew_thork_adventure"
    map_state = {
        "mode": "exploration",
        "room": "brewery_cellars",
        "graph": {"nodes": [], "edges": [], "party_location": "brewery_cellars"},
    }
    (inst / "map_state.json").write_text(json_lib.dumps(map_state))

    resp = client.get("/api/map/a_most_potent_brew_thork_adventure")
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "exploration"
    assert "terrain" not in data
    assert "grid" not in data


def test_get_map_merges_static_terrain(map_env):
    inst = map_env / "campaigns" / "a_most_potent_brew_thork_adventure"
    map_state = {
        "mode": "combat",
        "room": "brewery_cellars",
        "tokens": {"thork": {"x": 3, "y": 2, "hp": 7, "max_hp": 12, "conditions": [], "type": "party"}},
    }
    (inst / "map_state.json").write_text(json_lib.dumps(map_state))

    maps_dir = map_env / "available_campaigns" / "a_most_potent_brew" / "maps"
    maps_dir.mkdir(parents=True)
    static = {
        "room": "brewery_cellars",
        "label": "The Brewery Cellars",
        "grid": {"width": 14, "height": 10},
        "terrain": [{"type": "wall", "x1": 9, "y1": 0, "x2": 9, "y2": 7}],
    }
    (maps_dir / "brewery_cellars.json").write_text(json_lib.dumps(static))

    resp = client.get("/api/map/a_most_potent_brew_thork_adventure")
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "combat"
    assert data["grid"] == {"width": 14, "height": 10}
    assert data["label"] == "The Brewery Cellars"
    assert len(data["terrain"]) == 1
    assert data["terrain"][0]["type"] == "wall"
    assert "thork" in data["tokens"]


def test_get_map_dynamic_wins_on_conflict(map_env):
    """Dynamic fields override static fields on key collision."""
    inst = map_env / "campaigns" / "a_most_potent_brew_thork_adventure"
    (inst / "map_state.json").write_text(json_lib.dumps({"mode": "combat", "room": "brewery_cellars"}))

    maps_dir = map_env / "available_campaigns" / "a_most_potent_brew" / "maps"
    maps_dir.mkdir(parents=True)
    (maps_dir / "brewery_cellars.json").write_text(
        json_lib.dumps({"room": "brewery_cellars", "mode": "exploration", "grid": {"width": 14, "height": 10}})
    )

    data = client.get("/api/map/a_most_potent_brew_thork_adventure").json()
    assert data["mode"] == "combat"  # dynamic wins
    assert data["grid"]["width"] == 14  # static preserved
