"""DnD Dungeon Master Agent using Claude Agent SDK."""

import asyncio
from pathlib import Path
from typing import Any

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
)

from .logging_config import logger

# Project root directory (for skills and file operations)
PROJECT_ROOT = str(Path(__file__).parent.parent.resolve())

# Import domain logic from existing tools
from .tools.utility_tools import roll_dice as _roll_dice
from .tools.campaign_instance_tools import create_campaign_instance as _create_campaign_instance


# =============================================================================
# Custom Tools
# =============================================================================


@tool("roll_dice", "Roll dice using D&D notation (e.g., '1d20+5', '2d6')", {"notation": str})
async def roll_dice(args: dict[str, Any]) -> dict[str, Any]:
    notation = args["notation"]
    logger.debug(f"Rolling dice: {notation}")
    result = _roll_dice(notation)
    logger.info(f"Dice roll {notation} = {result}")
    return {"content": [{"type": "text", "text": str(result)}]}


@tool(
    "create_campaign_instance",
    "Create a new campaign instance from a template",
    {"campaign_template": str, "instance_name": str}
)
async def create_campaign_instance(args: dict[str, Any]) -> dict[str, Any]:
    campaign = args["campaign_template"]
    instance = args["instance_name"]
    logger.info(f"Creating campaign instance: {campaign}_{instance}")
    result = _create_campaign_instance(campaign, instance)
    if result.get("status") == "success":
        logger.info(f"Campaign instance created successfully: {result.get('instance_path')}")
    else:
        logger.error(f"Campaign creation failed: {result.get('error_message')}")
    return {"content": [{"type": "text", "text": str(result)}]}


# MCP server with custom tools
dnd_tools = create_sdk_mcp_server(
    name="dnd",
    version="1.0.0",
    tools=[roll_dice, create_campaign_instance],
)


# =============================================================================
# Agent
# =============================================================================

SYSTEM_PROMPT = """You are an experienced Dungeon Master for D&D 5th Edition.

## Available Tools

### Campaign Management
- roll_dice: Roll dice (1d20+5, 2d6, etc.)
- create_campaign_instance: Create a campaign instance from a template
- Skill (campaign-guide): Load campaigns, track progress through Acts/Beats, manage pre-generated characters

### Character Management (via character-management skill)
- Skill (character-management): Character creation, updates, and management
- Write: Create new character files (use with character-management skill)
- Edit: Update existing characters (use with character-management skill)
- Read: Read character files

### D&D Knowledge Base (via dnd-knowledge-store skill)
- Skill (dnd-knowledge-store): Access D&D 5e reference for classes, spells, monsters, and DM guidance
- Grep: Search knowledge files by pattern
- Glob: Find knowledge files by name pattern

## Campaign Tracking
When playing active campaigns, ALWAYS use campaign-guide skill after each conversation to check if anything need to be tracked.

## Guidelines
- Use campaign-guide skill to list available campaigns and create campaign instances
- Use character-management skill for character creation and updates (provides templates and patterns)
- Characters belong to campaign instances (stored in campaigns/[instance]/characters/)
- Use dnd-knowledge-store skill when players ask about D&D rules, spells, monsters, or class features
- Track campaign progress through Acts and Beats
"""


def get_options(permission_mode: str = "acceptEdits") -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        # ============================================
        # REQUIRED FOR SKILLS
        # ============================================
        cwd=PROJECT_ROOT,                          # Project root for skills discovery
        setting_sources=["user", "project"],       # Load skills + CLAUDE.md

        # ============================================
        # TOOLS CONFIGURATION
        # ============================================
        allowed_tools=[
            # Built-in tools (for skills)
            "Skill",                               # Enable skills
            "Read",                                # Read files
            "Write",                               # Create files (for characters)
            "Edit",                                # Update files (for characters)
            "Grep",                                # Search content
            "Glob",                                # Find files

            # Custom MCP tools
            "mcp__dnd__roll_dice",
            "mcp__dnd__create_campaign_instance",
        ],

        # ============================================
        # MCP SERVER
        # ============================================
        mcp_servers={"dnd": dnd_tools},

        # ============================================
        # OTHER SETTINGS
        # ============================================
        system_prompt=SYSTEM_PROMPT,
        permission_mode=permission_mode,
    )


async def run(prompt: str) -> str:
    """Run agent with a prompt."""
    from claude_agent_sdk import AssistantMessage, TextBlock
    import uuid

    logger.info(f"Starting agent query: {prompt[:100]}...")
    options = get_options()
    responses = []

    # Use async generator to work around SDK bug with MCP servers
    # See: https://github.com/anthropics/claude-agent-sdk-python/issues/266
    async def prompt_generator():
        session_id = str(uuid.uuid4())
        logger.debug(f"Session ID: {session_id}")
        yield {
            "type": "user",
            "message": {"role": "user", "content": prompt},
            "parent_tool_use_id": None,
            "session_id": session_id,
        }

    try:
        async for message in query(prompt=prompt_generator(), options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        responses.append(block.text)

        logger.info("Agent query completed successfully")
        return "\n".join(responses)

    except Exception as e:
        logger.error(f"Agent query failed: {e}", exc_info=True)
        raise


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
