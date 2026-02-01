"""DnD Dungeon Master Agent using Claude Agent SDK."""

import asyncio
from typing import Any

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
)

# Import domain logic from existing tools
from .tools.utility_tools import roll_dice as _roll_dice
from .tools.session_tools import create_game_session as _create_game_session
from .tools.character_tools.character_tools import (
    tool_create_character as _tool_create_character,
    tool_update_character as _tool_update_character,
)
from .tools.character_tools.character_validation import (
    tool_validate_character_readiness as _tool_validate_character_readiness,
)


# =============================================================================
# Custom Tools
# =============================================================================


@tool("roll_dice", "Roll dice using D&D notation (e.g., '1d20+5', '2d6')", {"notation": str})
async def roll_dice(args: dict[str, Any]) -> dict[str, Any]:
    result = _roll_dice(args["notation"])
    return {"content": [{"type": "text", "text": str(result)}]}


@tool("create_game_session", "Create a new game session", {"session_name": str, "dm_name": str})
async def create_game_session(args: dict[str, Any]) -> dict[str, Any]:
    result = _create_game_session(args["session_name"], args.get("dm_name", "DM"))
    return {"content": [{"type": "text", "text": str(result)}]}


@tool(
    "create_character",
    "Create a D&D 5e character",
    {
        "session_name": str,
        "character_name": str,
        "character_class": str,
        "race": str,
        "level": int,
    },
)
async def create_character(args: dict[str, Any]) -> dict[str, Any]:
    result = _tool_create_character(
        session_name=args["session_name"],
        character_name=args["character_name"],
        character_class=args.get("character_class"),
        race=args.get("race"),
        level=args.get("level", 1),
    )
    if result is None:
        return {"content": [{"type": "text", "text": "Failed to create character"}]}
    return {"content": [{"type": "text", "text": str(result)}]}


@tool("update_character", "Update a character", {"session_name": str, "character_name": str, "updates": dict})
async def update_character(args: dict[str, Any]) -> dict[str, Any]:
    result = _tool_update_character(
        session_name=args["session_name"],
        character_name=args["character_name"],
        updates=args["updates"],
    )
    if result is None:
        return {"content": [{"type": "text", "text": "Failed to update character"}]}
    return {"content": [{"type": "text", "text": str(result)}]}


@tool("validate_character", "Check if character is ready for adventure", {"session_name": str, "character_name": str})
async def validate_character(args: dict[str, Any]) -> dict[str, Any]:
    result = _tool_validate_character_readiness(
        session_name=args["session_name"],
        character_name=args["character_name"],
    )
    return {"content": [{"type": "text", "text": str(result)}]}


# MCP server with custom tools
dnd_tools = create_sdk_mcp_server(
    name="dnd",
    version="1.0.0",
    tools=[roll_dice, create_game_session, create_character, update_character, validate_character],
)


# =============================================================================
# Agent
# =============================================================================

SYSTEM_PROMPT = """You are an experienced Dungeon Master for D&D 5th Edition.

## Tools
- roll_dice: Roll dice (1d20+5, 2d6, etc.)
- create_game_session: Create a session before characters
- create_character: Create a character in a session
- update_character: Update character data
- validate_character: Check character readiness

Always create a session before creating characters.
"""


def get_options(permission_mode: str = "acceptEdits") -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        mcp_servers={"dnd": dnd_tools},
        allowed_tools=[
            "mcp__dnd__roll_dice",
            "mcp__dnd__create_game_session",
            "mcp__dnd__create_character",
            "mcp__dnd__update_character",
            "mcp__dnd__validate_character",
        ],
        system_prompt=SYSTEM_PROMPT,
        permission_mode=permission_mode,
    )


async def run(prompt: str) -> str:
    """Run agent with a prompt."""
    from claude_agent_sdk import AssistantMessage, TextBlock
    import uuid

    options = get_options()
    responses = []

    # Use async generator to work around SDK bug with MCP servers
    # See: https://github.com/anthropics/claude-agent-sdk-python/issues/266
    async def prompt_generator():
        yield {
            "type": "user",
            "message": {"role": "user", "content": prompt},
            "parent_tool_use_id": None,
            "session_id": str(uuid.uuid4()),
        }

    async for message in query(prompt=prompt_generator(), options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    responses.append(block.text)

    return "\n".join(responses)


def main():
    """CLI entry point."""
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(asyncio.run(run(prompt)))
    else:
        print("Usage: python -m dnd_dm_agent.claude_agent 'your prompt'")


if __name__ == "__main__":
    main()
