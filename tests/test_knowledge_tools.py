"""Tests for knowledge tools."""

import pytest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from dnd_dm_agent.tools.knowledge_tools import (
    get_knowledge_files,
    load_knowledge_file,
    lookup_knowledge,
    get_dnd_class_details,
    get_spell_details,
    get_monster_details,
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

MOCK_SPELL_CANTRIPS_CONTENT = """# Level 0 Spells (Cantrips)

## Fire Bolt
*Evocation cantrip*
A ranged spell attack that deals 1d10 fire damage.

## Mage Hand
*Conjuration cantrip*
A spectral hand that can manipulate objects.
"""

MOCK_SPELL_LEVEL1_CONTENT = """# Level 1 Spells

## Magic Missile
*1st-level evocation*
Creates three darts that each deal 1d4+1 force damage.

## Cure Wounds
*1st-level evocation*
Heals 1d8 + spellcasting modifier hit points.
"""

MOCK_MONSTERS_LOW_CR_CONTENT = """# Low CR Monsters

## Goblin
*Small humanoid (goblinoid), neutral evil*
AC 15, HP 7 (2d6), Speed 30 ft.

## Orc
*Medium humanoid (orc), chaotic evil*
AC 13, HP 15 (2d8 + 6), Speed 30 ft.
"""

MOCK_MONSTERS_DRAGONS_CONTENT = """# Dragons

## Red Dragon Wyrmling
*Medium dragon, chaotic evil*
AC 17, HP 75 (10d8 + 30), Speed 30 ft.

## Young Red Dragon
*Large dragon, chaotic evil*
AC 18, HP 178 (17d12 + 68), Speed 40 ft.
"""


@pytest.fixture
def mock_knowledge_files():
    """Mock knowledge files fixture with new folder structure."""
    mock_files = {
        "classes_5e": Path("/fake/path/classes_5e.md"),
        "session_management_guide": Path("/fake/path/session_management_guide.md"),
        "character_sheet_template": Path("/fake/path/character_sheet_template.md"),
        "player_handbook/spells/level_0_cantrips": Path("/fake/path/player_handbook/spells/level_0_cantrips.md"),
        "player_handbook/spells/level_1_spells": Path("/fake/path/player_handbook/spells/level_1_spells.md"),
        "monster_manual/low_cr_monsters": Path("/fake/path/monster_manual/low_cr_monsters.md"),
        "monster_manual/dragons": Path("/fake/path/monster_manual/dragons.md"),
        "player_handbook/classes/fighter": Path("/fake/path/player_handbook/classes/fighter.md"),
    }
    
    file_contents = {
        "classes_5e": MOCK_CLASSES_CONTENT,
        "session_management_guide": MOCK_GUIDE_CONTENT,
        "character_sheet_template": MOCK_TEMPLATE_CONTENT,
        "player_handbook/spells/level_0_cantrips": MOCK_SPELL_CANTRIPS_CONTENT,
        "player_handbook/spells/level_1_spells": MOCK_SPELL_LEVEL1_CONTENT,
        "monster_manual/low_cr_monsters": MOCK_MONSTERS_LOW_CR_CONTENT,
        "monster_manual/dragons": MOCK_MONSTERS_DRAGONS_CONTENT,
        "player_handbook/classes/fighter": "# Fighter Class\nMasters of martial combat.",
    }
    
    return mock_files, file_contents


def test_get_knowledge_files():
    """Test getting available knowledge files from real filesystem."""
    result = get_knowledge_files()
    
    # Should find at least the files we know exist
    assert len(result) >= 6
    assert "classes_5e" in result
    assert "session_management_guide" in result
    assert "character_sheet_template" in result
    assert "player_handbook/spells/level_0_cantrips" in result
    
    # Verify paths are actual Path objects
    for key, path in result.items():
        assert isinstance(path, Path)
        assert path.exists()


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
        # Use the key from mock_files to find content
        for key, path in mock_files.items():
            if path == file_path:
                return mock_open(read_data=file_contents[key])()
        raise FileNotFoundError()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = lookup_knowledge("NonexistentTerm")
            
            assert result["status"] == "success"
            assert result["query"] == "NonexistentTerm"
            assert len(result["results"]) == 0


def test_lookup_knowledge_folder_structure(mock_knowledge_files):
    """Test searching in nested folder structure."""
    mock_files, file_contents = mock_knowledge_files
    
    def mock_file_open(file_path, *args, **kwargs):
        # Use the key from mock_files to find content
        for key, path in mock_files.items():
            if path == file_path:
                return mock_open(read_data=file_contents[key])()
        raise FileNotFoundError()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = lookup_knowledge("Fire Bolt")
            
            assert result["status"] == "success"
            assert result["query"] == "Fire Bolt"
            assert len(result["results"]) == 1
            assert result["results"][0]["file"] == "player_handbook/spells/level_0_cantrips"


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
            assert result["total_files"] == 8
            
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


def test_lookup_knowledge_realistic_spell_search():
    """Test regex search with realistic multi-line spell content."""
    mock_files = {"player_handbook/spells/level_1_spells": Path("/fake/path/level_1_spells.md")}
    realistic_content = """# Level 1 Spells

First-level spells require a 1st-level spell slot to cast.

## Cure Wounds
*1st-level evocation*

**Casting Time:** 1 action  
**Range:** Touch  
**Components:** V, S  
**Duration:** Instantaneous

A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier. This spell has no effect on undead or constructs.

**At Higher Levels:** When you cast this spell using a spell slot of 2nd level or higher, the healing increases by 1d8 for each slot level above 1st.

## Magic Missile
*1st-level evocation*

**Casting Time:** 1 action  
**Range:** 120 feet  
**Components:** V, S  
**Duration:** Instantaneous

You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range. A dart deals 1d4 + 1 force damage to its target.

**At Higher Levels:** When you cast this spell using a spell slot of 2nd level or higher, the spell creates one more dart for each slot level above 1st.

## Shield
*1st-level abjuration*

**Casting Time:** 1 reaction  
**Range:** Self  
**Components:** V, S  
**Duration:** 1 round

An invisible barrier of magical force appears and protects you. Until the start of your next turn, you have a +5 bonus to AC.
"""
    
    def mock_file_open(file_path, *args, **kwargs):
        return mock_open(read_data=realistic_content)()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            # Test searching for damage patterns
            result = lookup_knowledge("1d[0-9]+")
            
            assert result["status"] == "success"
            assert len(result["results"]) == 1
            assert len(result["results"][0]["sections"]) == 2  # Cure Wounds and Magic Missile
            
            # Check that we get complete sections with all their content
            sections = result["results"][0]["sections"]
            cure_wounds = next(s for s in sections if "Cure Wounds" in s["header"])
            assert "Casting Time" in cure_wounds["content"]
            assert "At Higher Levels" in cure_wounds["content"]
            assert "1d8 + your spellcasting ability modifier" in cure_wounds["content"]
            
            # Test case insensitive search
            result2 = lookup_knowledge("EVOCATION")
            assert len(result2["results"][0]["sections"]) == 2  # Cure Wounds and Magic Missile
            
            # Test regex for spell schools
            result3 = lookup_knowledge(".*-level (evocation|abjuration)")
            assert len(result3["results"][0]["sections"]) == 3  # All three spells


def test_get_spell_details_success(mock_knowledge_files):
    """Test successfully getting spell details from spell files only."""
    mock_files, file_contents = mock_knowledge_files
    
    # Filter to only include spell files and other files for the test
    test_files = {
        "player_handbook/spells/level_0_cantrips": mock_files["player_handbook/spells/level_0_cantrips"], 
        "player_handbook/spells/level_1_spells": mock_files["player_handbook/spells/level_1_spells"],
        "monster_manual/dragons": mock_files["monster_manual/dragons"],
        "classes_5e": mock_files["classes_5e"],
    }
    
    def mock_file_open(file_path, *args, **kwargs):
        # Use the key from test_files to find content
        for key, path in test_files.items():
            if path == file_path:
                return mock_open(read_data=file_contents[key])()
        return mock_open(read_data="# Other Content")()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=test_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = get_spell_details("Fire Bolt")
            
            assert result["status"] == "success"
            assert result["spell_name"] == "Fire Bolt"
            assert "information" in result
            assert len(result["information"]) == 1
            assert "Fire Bolt" in result["information"][0]["header"]


def test_get_spell_details_not_found():
    """Test spell not found in spell files."""
    mock_files = {
        "player_handbook/spells/level_0_cantrips": Path("/fake/path/level_0_cantrips.md"),
    }
    
    def mock_file_open(file_path, *args, **kwargs):
        return mock_open(read_data="# Level 0 Spells\n\n## Other Spell\nNot the spell we want.")()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = get_spell_details("Nonexistent Spell")
            
            assert result["status"] == "error"
            assert "not found" in result["error_message"]


def test_get_monster_details_success(mock_knowledge_files):
    """Test successfully getting monster details from monster files only."""
    mock_files, file_contents = mock_knowledge_files
    
    # Filter to only include monster files and other files for the test
    test_files = {
        "monster_manual/low_cr_monsters": mock_files["monster_manual/low_cr_monsters"],
        "monster_manual/dragons": mock_files["monster_manual/dragons"],
        "player_handbook/spells/level_1_spells": mock_files["player_handbook/spells/level_1_spells"],
        "classes_5e": mock_files["classes_5e"],
    }
    
    def mock_file_open(file_path, *args, **kwargs):
        # Use the key from test_files to find content
        for key, path in test_files.items():
            if path == file_path:
                return mock_open(read_data=file_contents[key])()
        return mock_open(read_data="# Other Content")()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=test_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = get_monster_details("Goblin")
            
            assert result["status"] == "success"
            assert result["monster_name"] == "Goblin"
            assert "information" in result
            assert len(result["information"]) == 1
            assert "Goblin" in result["information"][0]["header"]


def test_get_monster_details_not_found():
    """Test monster not found in monster files."""
    mock_files = {
        "monster_manual/low_cr_monsters": Path("/fake/path/low_cr_monsters.md"),
    }
    
    def mock_file_open(file_path, *args, **kwargs):
        return mock_open(read_data="# Low CR Monsters\n\n## Other Monster\nNot the monster we want.")()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            result = get_monster_details("Nonexistent Monster")
            
            assert result["status"] == "error"
            assert "not found" in result["error_message"]


def test_specialized_functions_target_correct_files(mock_knowledge_files):
    """Test that specialized functions only search their target file types."""
    mock_files, file_contents = mock_knowledge_files
    
    # Override content to test cross-contamination - put spell names in monster files and vice versa
    test_file_contents = file_contents.copy()
    test_file_contents["monster_manual/low_cr_monsters"] = "# Monsters\n\n## Fire Bolt Monster\nA monster named after a spell."
    test_file_contents["player_handbook/spells/level_0_cantrips"] = "# Spells\n\n## Goblin Spell\nA spell named after a monster."
    
    def mock_file_open(file_path, *args, **kwargs):
        # Use the key from mock_files to find content
        for key, path in mock_files.items():
            if path == file_path:
                return mock_open(read_data=test_file_contents[key])()
        return mock_open(read_data="# Other Content")()
    
    with patch("dnd_dm_agent.tools.knowledge_tools.get_knowledge_files", return_value=mock_files):
        with patch("builtins.open", side_effect=mock_file_open):
            # Spell function should NOT find "Fire Bolt Monster" in monster files
            spell_result = get_spell_details("Fire Bolt")
            assert spell_result["status"] == "error"
            
            # Monster function should NOT find "Goblin Spell" in spell files  
            monster_result = get_monster_details("Goblin")
            assert monster_result["status"] == "error"