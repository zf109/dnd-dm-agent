"""Tests for Claude Agent SDK tool wrappers."""

import pytest


@pytest.mark.asyncio
async def test_roll_dice_wrapper():
    """Test roll_dice wrapper returns correct format."""
    from dnd_dm_agent.claude_agent import roll_dice

    result = await roll_dice({"notation": "1d20"})

    assert "content" in result
    assert result["content"][0]["type"] == "text"
    assert "success" in result["content"][0]["text"]
