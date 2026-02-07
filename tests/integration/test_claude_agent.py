"""Integration tests for Claude Agent SDK wrapper.

These tests require ANTHROPIC_API_KEY to be set and will make actual API calls.
"""

import pytest

@pytest.mark.asyncio
async def test_agent_dice_roll():
    """Test agent can roll dice using the roll_dice tool."""
    from dnd_dm_agent.claude_agent import run

    result = await run("Roll 2d6+3")

    # Check that we got a response
    assert result, "Expected non-empty response from agent"
    assert len(result) > 0, "Expected response text"

    # The response should mention rolling or dice results
    result_lower = result.lower()
    assert any(keyword in result_lower for keyword in ["roll", "dice", "total", "result"]), \
        f"Expected dice-related response, got: {result}"


@pytest.mark.asyncio
async def test_agent_knowledge_skill_classes():
    """Test agent can access D&D class knowledge via the dnd-knowledge-store skill."""
    from dnd_dm_agent.claude_agent import run

    result = await run("What abilities does a level 1 Fighter have in D&D 5e?")

    # Check that we got a response
    assert result, "Expected non-empty response from agent"
    assert len(result) > 0, "Expected response text"

    # The response should mention Fighter-related abilities
    result_lower = result.lower()
    assert any(keyword in result_lower for keyword in ["fighter", "fighting style", "second wind", "armor", "weapon"]), \
        f"Expected Fighter-related information, got: {result}"


@pytest.mark.asyncio
async def test_agent_knowledge_skill_spells():
    """Test agent can access spell knowledge from subdirectories via the dnd-knowledge-store skill."""
    from dnd_dm_agent.claude_agent import run

    result = await run("Tell me about the Magic Missile spell in D&D 5e")

    # Check that we got a response
    assert result, "Expected non-empty response from agent"
    assert len(result) > 0, "Expected response text"

    # The response should mention spell-related information
    result_lower = result.lower()
    assert any(keyword in result_lower for keyword in ["magic missile", "spell", "damage", "1st level", "force"]), \
        f"Expected Magic Missile spell information, got: {result}"


@pytest.mark.asyncio
async def test_agent_knowledge_skill_class_comparison():
    """Test agent can compare two classes by accessing knowledge for both."""
    from dnd_dm_agent.claude_agent import run

    result = await run("What's the difference between a wizard and a sorcerer?")

    # Check that we got a response
    assert result, "Expected non-empty response from agent"
    assert len(result) > 0, "Expected response text"

    # The response should mention both classes and their key differences
    result_lower = result.lower()

    # Should mention both classes
    assert "wizard" in result_lower, f"Expected mention of Wizard, got: {result}"
    assert "sorcerer" in result_lower, f"Expected mention of Sorcerer, got: {result}"

    # Should mention key distinguishing features
    wizard_features = ["intelligence", "spellbook", "study", "learn"]
    sorcerer_features = ["charisma", "metamagic", "born", "bloodline", "sorcery"]

    has_wizard_feature = any(feature in result_lower for feature in wizard_features)
    has_sorcerer_feature = any(feature in result_lower for feature in sorcerer_features)

    assert has_wizard_feature, f"Expected Wizard features (intelligence/spellbook/study), got: {result}"
    assert has_sorcerer_feature, f"Expected Sorcerer features (charisma/metamagic/born), got: {result}"


@pytest.mark.asyncio
async def test_character_management_create_and_update_wizard():
    """Test agent can create and update a spellcaster using character-management skill."""
    from dnd_dm_agent.claude_agent import run
    import os
    import shutil
    import re

    # Clean up any existing test campaign instance
    test_campaign_path = "campaigns/test_campaign"
    if os.path.exists(test_campaign_path):
        shutil.rmtree(test_campaign_path)

    # ===== PART 1: CREATE CHARACTER =====
    result = await run("Create a test campaign instance called 'test_campaign', then create a level 1 human wizard named Merlin")

    # Check that we got a response
    assert result, "Expected non-empty response from agent"
    assert len(result) > 0, "Expected response text"

    # Response should mention character creation
    result_lower = result.lower()
    assert "merlin" in result_lower, f"Expected mention of character name, got: {result}"
    assert any(keyword in result_lower for keyword in ["created", "character", "wizard"]), \
        f"Expected character creation confirmation, got: {result}"

    # Check that campaign instance was created
    assert os.path.exists(test_campaign_path), f"Expected campaign directory at {test_campaign_path}"
    assert os.path.exists(f"{test_campaign_path}/characters"), "Expected characters directory"

    # Check that character file was created
    character_file = f"{test_campaign_path}/characters/merlin.md"
    assert os.path.exists(character_file), f"Expected character file at {character_file}"

    # Read and validate initial character file content
    with open(character_file, 'r') as f:
        initial_content = f.read()
        content_lower = initial_content.lower()

        # Basic info
        assert "merlin" in content_lower, "Expected character name in file"
        assert "wizard" in content_lower, "Expected wizard class in file"
        assert "human" in content_lower, "Expected human race in file"
        assert "level" in content_lower and "1" in initial_content, "Expected level 1 in file"

        # Ability scores (wizard should have high INT)
        assert "intelligence" in content_lower or "int" in content_lower, "Expected intelligence ability"

        # Spellcasting section (key for wizards)
        assert "spellcasting" in content_lower or "spell" in content_lower, "Expected spellcasting section"
        assert "cantrip" in content_lower, "Expected cantrips for wizard"

        # Wizard features
        wizard_features = ["spellbook", "arcane recovery", "spell save dc"]
        has_wizard_feature = any(feature in content_lower for feature in wizard_features)
        assert has_wizard_feature, f"Expected wizard class features in character file"

        # Combat stats
        assert "hit points" in content_lower or "hp" in content_lower, "Expected HP section"
        assert "armor class" in content_lower or "ac" in content_lower, "Expected AC section"

        # Extract initial HP for comparison after update
        hp_match = re.search(r'(\d+)\s*/\s*(\d+)', initial_content)
        assert hp_match, "Expected to find HP in format 'current / max'"
        initial_current_hp = int(hp_match.group(1))
        initial_max_hp = int(hp_match.group(2))

    # ===== PART 2: UPDATE CHARACTER (TAKE DAMAGE) =====
    damage_amount = 3
    update_result = await run(f"Merlin from test_campaign takes {damage_amount} damage in combat")

    # Check update response
    assert update_result, "Expected non-empty response from update"
    update_lower = update_result.lower()
    assert any(keyword in update_lower for keyword in ["damage", "hp", "hit points", "health", str(damage_amount)]), \
        f"Expected damage-related response, got: {update_result}"

    # Read updated character file
    with open(character_file, 'r') as f:
        updated_content = f.read()

        # Extract updated HP
        updated_hp_match = re.search(r'(\d+)\s*/\s*(\d+)', updated_content)
        assert updated_hp_match, "Expected to find HP after update"
        updated_current_hp = int(updated_hp_match.group(1))
        updated_max_hp = int(updated_hp_match.group(2))

        # Verify HP was reduced by damage amount
        expected_hp = max(0, initial_current_hp - damage_amount)
        assert updated_current_hp == expected_hp, \
            f"Expected HP to be {expected_hp} after {damage_amount} damage, but got {updated_current_hp}"

        # Max HP should remain unchanged
        assert updated_max_hp == initial_max_hp, \
            f"Max HP should not change, expected {initial_max_hp}, got {updated_max_hp}"

    # ===== PART 3: ANOTHER UPDATE (CAST SPELL - USE SPELL SLOT) =====
    spell_result = await run("Merlin casts Magic Missile (1st level spell)")

    # Check spell response
    assert spell_result, "Expected non-empty response from spell casting"
    spell_lower = spell_result.lower()
    assert any(keyword in spell_lower for keyword in ["magic missile", "spell", "cast"]), \
        f"Expected spell-related response, got: {spell_result}"

    # Read character file after spell casting
    with open(character_file, 'r') as f:
        spell_content = f.read()
        spell_lower = spell_content.lower()

        # Should still have spellcasting section
        assert "spell" in spell_lower, "Expected spellcasting section to still exist"

        # File should be valid markdown structure
        assert "##" in spell_content, "Expected markdown headers in character file"

    # Clean up
    shutil.rmtree(test_campaign_path)
