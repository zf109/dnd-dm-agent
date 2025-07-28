"""Tests for character tools functions."""

import pytest
import tempfile
import json
from pathlib import Path
from dnd_dm_agent.tools.character_tools import (
    load_character_data,
    save_character_data,
    create_character_data,
    update_character_data,
    add_character_note_data,
    manage_character_create,
    manage_character_get,
    manage_character_update,
    manage_character_add_note,
    deep_update_dict,
)


@pytest.fixture
def temp_dir(monkeypatch):
    """Create a temporary directory and patch the SESSIONS_DIR."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Mock SESSIONS_DIR to point to our temp directory
        monkeypatch.setattr("dnd_dm_agent.tools.character_tools.SESSIONS_DIR", tmp_dir)
        yield tmp_dir


@pytest.fixture
def sample_character():
    """Sample character data for testing."""
    return {
        "basic_info": {"name": "Test Hero", "class": "Fighter", "level": 1},
        "notes": {"campaign_notes": [], "temporary_abilities": [], "important_npcs": []},
        "metadata": {"created_date": "2025-01-27T15:30:00", "last_updated": "2025-01-27T15:30:00"},
    }


# Tests for I/O functions
def test_save_and_load_character_data(temp_dir, sample_character):
    """Test saving and loading character data."""
    # Save character
    result = save_character_data("test_session", "Test Hero", sample_character, session_dir=temp_dir)
    assert result is True

    # Load character
    loaded_data = load_character_data("test_session", "Test Hero", session_dir=temp_dir)
    assert loaded_data is not None
    assert loaded_data["basic_info"]["name"] == "Test Hero"
    assert loaded_data["basic_info"]["class"] == "Fighter"
    assert "last_updated" in loaded_data["metadata"]


def test_load_nonexistent_character(temp_dir):
    """Test loading a character that doesn't exist."""
    result = load_character_data("test_session", "Nonexistent Hero", session_dir=temp_dir)
    assert result is None


# Tests for deep_update function
def test_deep_update_basic():
    """Test basic deep update functionality."""
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    updates = {"b": {"c": 99}, "e": 5}
    
    result = deep_update_dict(base, updates)
    
    # Should modify base in place and return it
    assert result is base
    assert base["a"] == 1  # Preserved
    assert base["b"]["c"] == 99  # Updated
    assert base["b"]["d"] == 3  # Preserved
    assert base["e"] == 5  # Added


def test_deep_update_nested_new_keys():
    """Test adding new nested keys."""
    base = {"existing": {"old": 1}}
    updates = {"existing": {"new": 2}, "completely_new": {"nested": {"deep": 3}}}
    
    deep_update_dict(base, updates)
    
    assert base["existing"]["old"] == 1  # Preserved
    assert base["existing"]["new"] == 2  # Added
    assert base["completely_new"]["nested"]["deep"] == 3  # Added completely new structure


def test_deep_update_empty_dicts():
    """Test deep update with empty dictionaries."""
    base = {"a": 1}
    updates = {}
    
    deep_update_dict(base, updates)
    assert base == {"a": 1}  # No changes
    
    # Test updating with empty nested dict
    base = {"nested": {"value": 1}}
    updates = {"nested": {}}
    
    deep_update_dict(base, updates)
    assert base["nested"]["value"] == 1  # Preserved, empty update doesn't remove


def test_deep_update_character_structure():
    """Test deep update with character-like data structure."""
    base = {
        "basic_info": {"name": "Hero", "level": 1},
        "combat_stats": {"hit_points": {"current": 10, "maximum": 10}},
        "ability_scores": {"strength": {"score": 15, "modifier": 2}}
    }
    
    updates = {
        "basic_info": {"level": 3},  # Update level, keep name
        "combat_stats": {"hit_points": {"current": 8}, "armor_class": 16},  # Update HP, add AC
        "ability_scores": {"strength": {"score": 16}, "dexterity": {"score": 14}}  # Update STR, add DEX
    }
    
    deep_update_dict(base, updates)
    
    # Check updates were applied correctly
    assert base["basic_info"]["name"] == "Hero"  # Preserved
    assert base["basic_info"]["level"] == 3  # Updated
    assert base["combat_stats"]["hit_points"]["current"] == 8  # Updated
    assert base["combat_stats"]["hit_points"]["maximum"] == 10  # Preserved
    assert base["combat_stats"]["armor_class"] == 16  # Added
    assert base["ability_scores"]["strength"]["score"] == 16  # Updated
    assert base["ability_scores"]["strength"]["modifier"] == 2  # Preserved
    assert base["ability_scores"]["dexterity"]["score"] == 14  # Added


# Tests for pure functions (no I/O)
def test_create_character_data_with_defaults():
    """Test creating character data with default values."""
    character = create_character_data("Test Hero")

    # Check basic info
    assert character["basic_info"]["name"] == "Test Hero"
    assert character["basic_info"]["class"] == "Fighter"
    assert character["basic_info"]["level"] == 1
    assert character["basic_info"]["race"] == "Human"
    assert character["basic_info"]["background"] == "Soldier"
    assert character["basic_info"]["alignment"] == "Neutral"

    # Check ability scores have defaults
    assert character["ability_scores"]["strength"]["score"] == 15
    assert character["ability_scores"]["dexterity"]["score"] == 14
    assert character["ability_scores"]["constitution"]["score"] == 13

    # Check modifiers are calculated
    assert character["ability_scores"]["strength"]["modifier"] == 2  # (15-10)//2
    assert character["ability_scores"]["dexterity"]["modifier"] == 2  # (14-10)//2

    # Check combat stats
    assert character["proficiency_bonus"] == 2  # Level 1
    assert character["combat_stats"]["initiative"] == 2  # Dex modifier


def test_create_character_data_with_custom_values():
    """Test creating character data with custom values."""
    character = create_character_data(
        "Custom Hero",
        character_class="Wizard",
        race="Elf",
        background="Noble",
        alignment="Chaotic Good",
        level=3,
        strength=12,
        intelligence=18,
        hit_points_max=24,
        armor_class=13,
    )

    # Check custom values were set
    assert character["basic_info"]["class"] == "Wizard"
    assert character["basic_info"]["race"] == "Elf"
    assert character["basic_info"]["background"] == "Noble"
    assert character["basic_info"]["alignment"] == "Chaotic Good"
    assert character["basic_info"]["level"] == 3

    # Check custom ability scores
    assert character["ability_scores"]["strength"]["score"] == 12
    assert character["ability_scores"]["intelligence"]["score"] == 18
    assert character["ability_scores"]["intelligence"]["modifier"] == 4  # (18-10)//2


def test_update_character_data():
    """Test updating character data."""
    original_character = create_character_data("Test Hero")

    updates = {
        "basic_info": {"level": 3},
        "ability_scores": {
            "intelligence": {
                "score": 16,
                "modifier": 2,
                "saving_throw": 1,
                "proficient": False,
            },
            "dexterity": {"score": 14},
        },
        "combat_stats": {"hit_points": {"current": 20}},
    }

    updated_character = update_character_data(original_character, updates)

    # Check updates were applied
    assert updated_character["basic_info"]["level"] == 3
    assert updated_character["ability_scores"]["intelligence"]["score"] == 16
    assert updated_character["ability_scores"]["intelligence"]["modifier"] == 2
    assert updated_character["combat_stats"]["hit_points"]["current"] == 20

    # Check original data is preserved
    assert updated_character["basic_info"]["name"] == "Test Hero"
    assert updated_character["combat_stats"]["hit_points"]["maximum"] == 10  # Original value


def test_add_character_note_data():
    """Test adding note to character data."""
    original_character = create_character_data("Test Hero")

    updated_character = add_character_note_data(
        original_character, "Found a secret door", "campaign_notes", "test_session"
    )

    # Check note was added
    assert len(updated_character["notes"]["campaign_notes"]) == 1
    assert updated_character["notes"]["campaign_notes"][0]["note"] == "Found a secret door"
    assert updated_character["notes"]["campaign_notes"][0]["session"] == "test_session"
    assert "timestamp" in updated_character["notes"]["campaign_notes"][0]


def test_add_character_note_data_different_types():
    """Test adding different types of notes."""
    original_character = create_character_data("Test Hero")

    # Add different note types
    character_with_campaign_note = add_character_note_data(original_character, "Campaign event", "campaign_notes")
    character_with_ability_note = add_character_note_data(
        character_with_campaign_note, "Has inspiration", "temporary_abilities"
    )
    character_with_npc_note = add_character_note_data(
        character_with_ability_note, "Met the blacksmith", "important_npcs"
    )

    # Check all notes were added
    assert len(character_with_npc_note["notes"]["campaign_notes"]) == 1
    assert len(character_with_npc_note["notes"]["temporary_abilities"]) == 1
    assert len(character_with_npc_note["notes"]["important_npcs"]) == 1




# Tests for individual manage_character functions
def test_manage_character_create_function(temp_dir):
    """Test manage_character_create function directly."""
    character = manage_character_create(
        session_name="test_session",
        character_name="Direct Hero",
        character_class="Rogue",
        race="Halfling",
        background="Criminal",
        alignment="Chaotic Neutral",
        level=2,
        strength=12,
        dexterity=18,
        constitution=14,
        intelligence=13,
        wisdom=12,
        charisma=15,
        hit_points_max=18,
        armor_class=16,
    )

    assert character is not None
    assert character["basic_info"]["name"] == "Direct Hero"
    assert character["basic_info"]["class"] == "Rogue"
    assert character["basic_info"]["race"] == "Halfling"
    assert character["basic_info"]["background"] == "Criminal"
    assert character["basic_info"]["alignment"] == "Chaotic Neutral"
    assert character["basic_info"]["level"] == 2
    assert character["ability_scores"]["strength"]["score"] == 12
    assert character["ability_scores"]["dexterity"]["score"] == 18
    assert character["combat_stats"]["hit_points"]["maximum"] == 18
    assert character["combat_stats"]["armor_class"] == 16

    # Check character was saved
    loaded_character = load_character_data("test_session", "Direct Hero", session_dir=temp_dir)
    assert loaded_character is not None
    assert loaded_character["basic_info"]["name"] == "Direct Hero"


def test_manage_character_get_function(temp_dir, sample_character):
    """Test manage_character_get function directly."""
    # First save a character
    save_character_data("test_session", "Get Hero", sample_character, session_dir=temp_dir)

    # Then get it via manage_character_get
    character = manage_character_get(session_name="test_session", character_name="Get Hero")

    assert character is not None
    assert character["basic_info"]["name"] == "Test Hero"  # From sample_character fixture


def test_manage_character_get_nonexistent(temp_dir):
    """Test manage_character_get with nonexistent character."""
    character = manage_character_get(session_name="test_session", character_name="Nonexistent Hero")
    assert character is None


def test_manage_character_update_function(temp_dir, sample_character):
    """Test manage_character_update function directly."""
    # First save a character
    save_character_data("test_session", "Update Hero", sample_character, session_dir=temp_dir)

    # Update via manage_character_update
    updates = {
        "basic_info": {"level": 7},
        "combat_stats": {"armor_class": 19},
        "ability_scores": {
            "strength": {"score": 18},
            "intelligence": {"score": 16}
        }
    }
    
    updated_character = manage_character_update(
        session_name="test_session",
        character_name="Update Hero",
        updates=updates
    )

    assert updated_character is not None
    assert updated_character["basic_info"]["level"] == 7
    assert updated_character["combat_stats"]["armor_class"] == 19
    assert updated_character["ability_scores"]["strength"]["score"] == 18
    assert updated_character["ability_scores"]["intelligence"]["score"] == 16


def test_manage_character_update_nonexistent(temp_dir):
    """Test manage_character_update with nonexistent character."""
    updates = {"basic_info": {"level": 5}}
    
    result = manage_character_update(
        session_name="test_session",
        character_name="Nonexistent Hero",
        updates=updates
    )
    assert result is None


def test_manage_character_add_note_function(temp_dir, sample_character):
    """Test manage_character_add_note function directly."""
    # First save a character
    save_character_data("test_session", "Note Hero", sample_character, session_dir=temp_dir)

    # Add note via manage_character_add_note
    updated_character = manage_character_add_note(
        session_name="test_session",
        character_name="Note Hero",
        note="Direct function call note",
        note_type="campaign_notes"
    )

    assert updated_character is not None
    assert len(updated_character["notes"]["campaign_notes"]) == 1
    assert updated_character["notes"]["campaign_notes"][0]["note"] == "Direct function call note"
    assert "timestamp" in updated_character["notes"]["campaign_notes"][0]


def test_manage_character_add_note_nonexistent(temp_dir):
    """Test manage_character_add_note with nonexistent character."""
    result = manage_character_add_note(
        session_name="test_session",
        character_name="Nonexistent Hero",
        note="Test note",
        note_type="campaign_notes"
    )
    assert result is None


def test_manage_character_create_with_defaults(temp_dir):
    """Test manage_character_create with default values."""
    character = manage_character_create(
        session_name="test_session",
        character_name="Default Hero"
    )

    assert character is not None
    assert character["basic_info"]["name"] == "Default Hero"
    assert character["basic_info"]["class"] == "Fighter"  # Default
    assert character["basic_info"]["race"] == "Human"     # Default
    assert character["basic_info"]["background"] == "Soldier"  # Default
    assert character["basic_info"]["alignment"] == "Neutral"   # Default
    assert character["basic_info"]["level"] == 1         # Default
    assert character["ability_scores"]["strength"]["score"] == 15  # Default
    assert character["ability_scores"]["dexterity"]["score"] == 14  # Default
    assert character["combat_stats"]["hit_points"]["maximum"] == 10  # Default
    assert character["combat_stats"]["armor_class"] == 15  # Default
