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
