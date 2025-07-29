"""Tests for utility tools - dice rolling and game state management."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, mock_open, patch

from dnd_dm_agent.tools.utility_tools import parse_dice_notation, roll_dice, manage_game_state


# Dice rolling tests (moved from test_dice.py)
def test_roll_dice_basic():
    """Test basic dice rolling."""
    result = roll_dice("2d6+3")
    assert result["notation"] == "2d6+3"
    assert len(result["individual_rolls"]) == 2
    assert all(1 <= roll <= 6 for roll in result["individual_rolls"])
    assert result["total"] == sum(result["individual_rolls"]) + 3
    assert result["modifier"] == 3


def test_parse_dice_notation():
    """Test parsing various dice notations."""
    assert parse_dice_notation("1d20") == (1, 20, 0)
    assert parse_dice_notation("2d6+3") == (2, 6, 3)
    assert parse_dice_notation("d8-2") == (1, 8, -2)
    assert parse_dice_notation("3d4") == (3, 4, 0)


# Game state management tests
@pytest.fixture
def mock_session_metadata():
    """Mock session metadata for testing."""
    return {
        "session_name": "Test Campaign",
        "dm_name": "Test DM",
        "created_date": "2025-01-27T15:30:00",
        "last_played": "2025-01-27T18:45:00",
        "characters": ["Thorin", "Elara"],
        "session_notes": "",
        "current_location": "Goblin Cave",
        "current_scene": "The party stands at the cave entrance",
        "history": [
            {
                "timestamp": "2025-01-27T18:00:00",
                "type": "location_change",
                "from": "Starting Location",
                "to": "Goblin Cave"
            }
        ],
    }


def test_manage_game_state_get_state(mock_session_metadata):
    """Test getting current game state."""
    session_name = "Test Campaign"
    
    # Mock the path operations
    mock_session_path = MagicMock()
    mock_session_path.exists.return_value = True
    mock_metadata_path = MagicMock()
    mock_session_path.__truediv__.return_value = mock_metadata_path  # Enable session_path / "file"
    
    with patch("dnd_dm_agent.tools.utility_tools.SESSIONS_DIR") as mock_sessions_dir:
        mock_sessions_dir.__truediv__.return_value = mock_session_path
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_session_metadata))):
            result = manage_game_state(session_name, "get_state")
            
            assert result["status"] == "success"
            assert result["current_location"] == "Goblin Cave"
            assert result["current_scene"] == "The party stands at the cave entrance"
            assert result["characters"] == ["Thorin", "Elara"]
            assert result["session_name"] == session_name
            assert "history" in result
            assert len(result["history"]) == 1


def test_manage_game_state_update_location(mock_session_metadata):
    """Test updating game location."""
    session_name = "Test Campaign"
    new_location = "Dragon's Lair"
    
    # Mock the path operations
    mock_session_path = MagicMock()
    mock_session_path.exists.return_value = True
    mock_metadata_path = MagicMock()
    mock_session_path.__truediv__.return_value = mock_metadata_path
    
    mock_file = mock_open(read_data=json.dumps(mock_session_metadata))
    
    with patch("dnd_dm_agent.tools.utility_tools.SESSIONS_DIR") as mock_sessions_dir:
        mock_sessions_dir.__truediv__.return_value = mock_session_path
        with patch("builtins.open", mock_file):
            result = manage_game_state(session_name, "update_location", location=new_location)
            
            assert result["status"] == "success"
            assert result["location"] == new_location
            
            # Verify that the mock file was written to (history was added)
            assert mock_file().write.called


def test_manage_game_state_update_scene(mock_session_metadata):
    """Test updating game scene."""
    session_name = "Test Campaign"
    new_scene = "Ancient runes glow on the stone walls as you approach the altar"
    
    # Mock the path operations
    mock_session_path = MagicMock()
    mock_session_path.exists.return_value = True
    mock_metadata_path = MagicMock()
    mock_session_path.__truediv__.return_value = mock_metadata_path
    
    mock_file = mock_open(read_data=json.dumps(mock_session_metadata))
    
    with patch("dnd_dm_agent.tools.utility_tools.SESSIONS_DIR") as mock_sessions_dir:
        mock_sessions_dir.__truediv__.return_value = mock_session_path
        with patch("builtins.open", mock_file):
            result = manage_game_state(session_name, "update_scene", scene=new_scene)
            
            assert result["status"] == "success"
            assert result["scene"] == new_scene
            
            # Verify that the mock file was written to (history was added)
            assert mock_file().write.called


def test_manage_game_state_session_not_found():
    """Test error when session doesn't exist."""
    session_name = "Nonexistent Campaign"
    
    # Mock the path operations
    mock_session_path = MagicMock()
    mock_session_path.exists.return_value = False
    
    with patch("dnd_dm_agent.tools.utility_tools.SESSIONS_DIR") as mock_sessions_dir:
        mock_sessions_dir.__truediv__.return_value = mock_session_path
        result = manage_game_state(session_name, "get_state")
        
        assert result["status"] == "error"
        assert "does not exist" in result["error_message"]


def test_manage_game_state_invalid_action(mock_session_metadata):
    """Test error with invalid action."""
    session_name = "Test Campaign"
    
    # Mock the path operations
    mock_session_path = MagicMock()
    mock_session_path.exists.return_value = True
    mock_metadata_path = MagicMock()
    mock_session_path.__truediv__.return_value = mock_metadata_path
    
    with patch("dnd_dm_agent.tools.utility_tools.SESSIONS_DIR") as mock_sessions_dir:
        mock_sessions_dir.__truediv__.return_value = mock_session_path
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_session_metadata))):
            result = manage_game_state(session_name, "invalid_action")
            
            assert result["status"] == "error"
            assert "Invalid action" in result["error_message"]


def test_manage_game_state_missing_parameters(mock_session_metadata):
    """Test error when required parameters are missing."""
    session_name = "Test Campaign"
    
    # Mock the path operations
    mock_session_path = MagicMock()
    mock_session_path.exists.return_value = True
    mock_metadata_path = MagicMock()
    mock_session_path.__truediv__.return_value = mock_metadata_path
    
    with patch("dnd_dm_agent.tools.utility_tools.SESSIONS_DIR") as mock_sessions_dir:
        mock_sessions_dir.__truediv__.return_value = mock_session_path
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_session_metadata))):
            # Try to update location without providing location parameter
            result = manage_game_state(session_name, "update_location")
            
            assert result["status"] == "error"
            assert "missing required parameters" in result["error_message"]


def test_manage_game_state_history_tracking():
    """Test that history entries are created correctly."""
    session_name = "Test Campaign"
    
    # Mock metadata without history field to test backward compatibility
    metadata_without_history = {
        "session_name": "Test Campaign",
        "current_location": "Old Location",
        "current_scene": "Old scene",
        "characters": [],
    }
    
    # Mock the path operations
    mock_session_path = MagicMock()
    mock_session_path.exists.return_value = True
    mock_metadata_path = MagicMock()
    mock_session_path.__truediv__.return_value = mock_metadata_path
    
    with patch("dnd_dm_agent.tools.utility_tools.SESSIONS_DIR") as mock_sessions_dir:
        mock_sessions_dir.__truediv__.return_value = mock_session_path
        
        # Test location change creates history entry
        with patch("builtins.open", mock_open(read_data=json.dumps(metadata_without_history))):
            result = manage_game_state(session_name, "update_location", location="New Location")
            
            assert result["status"] == "success"
            assert result["location"] == "New Location"