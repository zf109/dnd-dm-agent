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
