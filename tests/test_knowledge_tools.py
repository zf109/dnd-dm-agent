"""Tests for knowledge tools."""

import pytest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from dnd_dm_agent.tools.knowledge_tools import (
    get_knowledge_files,
    load_knowledge_file,
    lookup_knowledge,
    get_dnd_class_details,
    get_dm_guidance,
    list_available_knowledge,
)


# Mock content for testing
MOCK_CLASSES_CONTENT = """# Fighter
A master of martial combat, skilled with various weapons and armor.

## Class Features
- Fighting Style
- Second Wind

# Wizard
A scholarly magic-user capable of manipulating the forces of magic.

## Class Features
- Spellcasting
- Arcane Recovery
"""

MOCK_GUIDE_CONTENT = """# Session Management Guide
Guide for running D&D sessions effectively.

## Combat
Tips for running combat encounters smoothly.
- Initiative tracking
- Action economy

## Roleplay
Encouraging player interaction and character development.
- Voice and mannerisms
- Character motivations
"""

MOCK_TEMPLATE_CONTENT = """# Character Sheet Template
Template for creating character sheets.

## Basic Information
- Name
- Class
- Race
"""


@pytest.fixture
def mock_knowledge_files():
    """Mock knowledge files fixture."""
    mock_files = {
        "classes_5e": Path("/fake/path/classes_5e.md"),
        "session_management_guide": Path("/fake/path/session_management_guide.md"),
        "character_sheet_template": Path("/fake/path/character_sheet_template.md"),
    }
    
    file_contents = {
        "classes_5e": MOCK_CLASSES_CONTENT,
        "session_management_guide": MOCK_GUIDE_CONTENT,
        "character_sheet_template": MOCK_TEMPLATE_CONTENT,
    }
    
    return mock_files, file_contents


def test_get_knowledge_files(mock_knowledge_files):
    """Test getting available knowledge files."""
    mock_files, _ = mock_knowledge_files
    mock_dir = Mock()
    mock_dir.exists.return_value = True
    mock_dir.glob.return_value = list(mock_files.values())
    
    with patch("dnd_dm_agent.tools.knowledge_tools.Path") as mock_path:
        mock_path.return_value.parent.parent.__truediv__.return_value = mock_dir
        
        result = get_knowledge_files()
        
        assert len(result) == 3
        assert "classes_5e" in result
        assert "session_management_guide" in result
        assert "character_sheet_template" in result


def test_get_knowledge_files_no_directory():
    """Test getting knowledge files when directory doesn't exist."""
    mock_dir = Mock()
    mock_dir.exists.return_value = False
    
    with patch("dnd_dm_agent.tools.knowledge_tools.Path") as mock_path:
        mock_path.return_value.parent.parent.__truediv__.return_value = mock_dir
        
        result = get_knowledge_files()
        
        assert result == {}


def test_load_knowledge_file_success(mock_knowledge_files):
    """Test successfully loading a knowledge file."""
    mock_files, file_contents = mock_knowledge_files
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", mock_open(read_data=file_contents["classes_5e"])):
            result = load_knowledge_file("classes_5e")
            
            assert result["status"] == "success"
            assert result["filename"] == "classes_5e"
            assert result["content"] == file_contents["classes_5e"]
            assert "file_path" in result


def test_load_knowledge_file_not_found(mock_knowledge_files):
    """Test loading a non-existent knowledge file."""
    mock_files, _ = mock_knowledge_files
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        result = load_knowledge_file("nonexistent")
        
        assert result["status"] == "error"
        assert "not found" in result["error_message"]
        assert "classes_5e" in result["error_message"]  # Should list available files


def test_lookup_knowledge_all_files(mock_knowledge_files):
    """Test searching across all knowledge files."""
    mock_files, file_contents = mock_knowledge_files
    
    def mock_file_open(file_path, *args, **kwargs):
        filename = file_path.stem
        if filename in file_contents:
            return mock_open(read_data=file_contents[filename])()
        raise FileNotFoundError()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = lookup_knowledge("Fighter")
            
            assert result["status"] == "success"
            assert result["query"] == "Fighter"
            assert len(result["results"]) == 1
            assert result["results"][0]["file"] == "classes_5e"
            assert len(result["results"][0]["sections"]) > 0


def test_lookup_knowledge_specific_files(mock_knowledge_files):
    """Test searching specific knowledge files."""
    mock_files, file_contents = mock_knowledge_files
    
    def mock_file_open(file_path, *args, **kwargs):
        filename = file_path.stem
        if filename in file_contents:
            return mock_open(read_data=file_contents[filename])()
        raise FileNotFoundError()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = lookup_knowledge("Combat", specific_files=["session_management_guide"])
            
            assert result["status"] == "success"
            assert result["query"] == "Combat"
            assert len(result["results"]) == 1
            assert result["results"][0]["file"] == "session_management_guide"


def test_lookup_knowledge_no_matches(mock_knowledge_files):
    """Test searching with no matching results."""
    mock_files, file_contents = mock_knowledge_files
    
    def mock_file_open(file_path, *args, **kwargs):
        filename = file_path.stem
        if filename in file_contents:
            return mock_open(read_data=file_contents[filename])()
        raise FileNotFoundError()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = lookup_knowledge("NonexistentTerm")
            
            assert result["status"] == "success"
            assert result["query"] == "NonexistentTerm"
            assert len(result["results"]) == 0


def test_get_dnd_class_details_success(mock_knowledge_files):
    """Test getting class details successfully."""
    mock_files, file_contents = mock_knowledge_files
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", mock_open(read_data=file_contents["classes_5e"])):
            result = get_dnd_class_details("Fighter")
            
            assert result["status"] == "success"
            assert result["class_name"] == "Fighter"
            assert "information" in result
            assert len(result["information"]) > 0


def test_get_dnd_class_details_not_found(mock_knowledge_files):
    """Test getting class details for non-existent class."""
    mock_files, file_contents = mock_knowledge_files
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", mock_open(read_data=file_contents["classes_5e"])):
            result = get_dnd_class_details("NonexistentClass")
            
            assert result["status"] == "error"
            assert "not found" in result["error_message"]


def test_get_dm_guidance_with_topic(mock_knowledge_files):
    """Test getting DM guidance for specific topic."""
    mock_files, file_contents = mock_knowledge_files
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", mock_open(read_data=file_contents["session_management_guide"])):
            result = get_dm_guidance("Combat")
            
            assert result["status"] == "success"
            assert result["topic"] == "Combat"
            assert "guidance" in result
            assert len(result["guidance"]) > 0


def test_get_dm_guidance_without_topic(mock_knowledge_files):
    """Test getting full DM guidance."""
    mock_files, file_contents = mock_knowledge_files
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", mock_open(read_data=file_contents["session_management_guide"])):
            result = get_dm_guidance()
            
            assert result["status"] == "success"
            assert "content" in result
            assert result["content"] == file_contents["session_management_guide"]


def test_get_dm_guidance_topic_not_found(mock_knowledge_files):
    """Test getting DM guidance for non-existent topic."""
    mock_files, file_contents = mock_knowledge_files
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", mock_open(read_data=file_contents["session_management_guide"])):
            result = get_dm_guidance("NonexistentTopic")
            
            assert result["status"] == "error"
            assert "not found" in result["error_message"]


def test_list_available_knowledge(mock_knowledge_files):
    """Test listing available knowledge files."""
    mock_files, file_contents = mock_knowledge_files
    
    def mock_file_open(file_path, *args, **kwargs):
        filename = file_path.stem
        if filename in file_contents:
            return mock_open(read_data=file_contents[filename])()
        raise FileNotFoundError()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = list_available_knowledge()
            
            assert result["status"] == "success"
            assert "available_files" in result
            assert result["total_files"] == 3
            
            # Check that descriptions are truncated to 200 chars + "..."
            for filename, info in result["available_files"].items():
                assert "path" in info
                assert "description" in info
                if len(file_contents[filename]) > 200:
                    assert info["description"].endswith("...")
                    assert len(info["description"]) <= 203  # 200 + "..."


def test_list_available_knowledge_truncation():
    """Test that descriptions are properly truncated to 200 characters."""
    # Create a long content string
    long_content = "A" * 300 + "\nMore content here"
    mock_files = {"test_file": Path("/fake/path/test_file.md")}
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", mock_open(read_data=long_content)):
            result = list_available_knowledge()
            
            assert result["status"] == "success"
            description = result["available_files"]["test_file"]["description"]
            assert description.endswith("...")
            assert len(description) == 203  # 200 chars + "..."