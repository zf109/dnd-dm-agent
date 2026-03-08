"""DnD Dungeon Master Agent using Claude Agent SDK."""

import asyncio
import sys
import uuid
from pathlib import Path
from typing import Any, AsyncIterator

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    tool,
    create_sdk_mcp_server,
)

from .logging_config import logger, dm_logger, bookkeeping_logger

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
    dm_logger.debug(f"Rolling dice: {notation}")
    result = _roll_dice(notation)
    dm_logger.info(f"Dice roll {notation} = {result}")
    return {"content": [{"type": "text", "text": str(result)}]}


@tool(
    "create_campaign_instance",
    "Create a new campaign instance from a template",
    {"campaign_template": str, "instance_name": str}
)
async def create_campaign_instance(args: dict[str, Any]) -> dict[str, Any]:
    campaign = args["campaign_template"]
    instance = args["instance_name"]
    dm_logger.info(f"Creating campaign instance: {campaign}_{instance}")
    result = _create_campaign_instance(campaign, instance)
    if result.get("status") == "success":
        dm_logger.info(f"Campaign instance created successfully: {result.get('instance_path')}")
    else:
        dm_logger.error(f"Campaign creation failed: {result.get('error_message')}")
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

## Guidelines
- Use campaign-guide skill to list available campaigns and create campaign instances
- Use character-management skill for character creation and updates (provides templates and patterns)
- Characters belong to campaign instances (stored in campaigns/[instance]/characters/)
- Use dnd-knowledge-store skill when players ask about D&D rules, spells, monsters, or class features
- Focus on narration and gameplay — bookkeeping (character sheet updates, campaign progress) is handled separately after each turn
"""


def get_options(permission_mode: str = "acceptEdits", campaign: str = "", character: str = "") -> ClaudeAgentOptions:
    system_prompt = SYSTEM_PROMPT
    if campaign and character:
        system_prompt += (
            f"\n\n## Current Session\n"
            f"Campaign: {campaign}\n"
            f"Active character: {character}\n"
            f"Always maintain awareness of this campaign and character throughout the session. "
            f"Load the campaign via the campaign-guide skill at the start of the session."
        )

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
        system_prompt=system_prompt,
        permission_mode=permission_mode,
    )


def process_message(message: Any) -> str | None:
    """
    Process a single message and apply logging.
    Returns text content if it's a TextBlock, None otherwise.
    This function can be imported and used by REPL or other interfaces.
    """
    if isinstance(message, AssistantMessage):
        text_content = None
        for block in message.content:
            if isinstance(block, TextBlock):
                text_content = block.text
            elif isinstance(block, ToolUseBlock):
                logger.info(f"Tool invoked: {block.name} with input: {block.input}")

                # Note: Skills are NOT tools - they're instruction sets loaded into context
                # This logging is kept for backward compatibility but will likely never trigger
                if block.name == "Skill":
                    skill_name = block.input.get("skill", "unknown")
                    skill_args = block.input.get("args", "")
                    logger.info(f"Skill invoked: {skill_name}" +
                               (f" with args: {skill_args}" if skill_args else ""))
        return text_content
    return None


BOOKKEEPING_SYSTEM_PROMPT = """You are a silent D&D session recorder. Your only job is to update files based on what happened in the last exchange.

- HP, conditions, spell slots, or equipment changed → update character sheet
- Story beat or objective completed → mark it in campaign progress
- New NPC or location encountered for the first time → record it

Do NOT narrate or explain. Only use tools if something actually changed."""


def get_bookkeeping_options(campaign: str = "", character: str = "") -> ClaudeAgentOptions:
    system = BOOKKEEPING_SYSTEM_PROMPT
    if campaign and character:
        system += f"\n\nCampaign: {campaign}\nCharacter: {character}"
    return ClaudeAgentOptions(
        cwd=PROJECT_ROOT,
        setting_sources=["user", "project"],
        allowed_tools=["Skill", "Read", "Write", "Edit", "Glob"],
        system_prompt=system,
        permission_mode="bypassPermissions",
    )


async def run_bookkeeping_subagent(
    user_msg: str,
    dm_response: str,
    campaign: str = "",
    character: str = "",
) -> AsyncIterator[Any]:
    """
    Bookkeeping subagent with fresh context per turn.
    Yields messages so callers can react to tool-use events (e.g. forward to UI).
    Domain logic is delegated to campaign-guide and character-management skills.
    """
    handoff = (
        f"## Last Exchange\n\n"
        f"**User:** {user_msg}\n\n"
        f"**DM:** {dm_response}\n\n"
        f"Use the campaign-guide and character-management skills to update any files that changed."
    )
    bookkeeping_logger.info("Starting bookkeeping subagent")
    async with ClaudeSDKClient(options=get_bookkeeping_options(campaign, character)) as bk:
        await bk.query(handoff)
        async for message in bk.receive_response():
            process_message(message)
            yield message
    bookkeeping_logger.info("Bookkeeping subagent complete")


async def run_query(prompt: str, options: ClaudeAgentOptions | None = None) -> AsyncIterator[Any]:
    """
    Run agent query with logging applied to all messages.
    This is an async generator that yields messages with logging applied.

    This function can be imported and used by REPL or other interfaces to get
    the same logging behavior as the CLI.

    Usage:
        from dnd_dm_agent.claude_agent import run_query, get_options

        async for message in run_query("Your prompt", get_options()):
            # All messages have logging applied automatically
            print(message)
    """
    if options is None:
        options = get_options()

    dm_logger.info(f"Starting agent query: {prompt[:100]}...")

    # Use async generator to work around SDK bug with MCP servers
    # See: https://github.com/anthropics/claude-agent-sdk-python/issues/266
    async def prompt_generator():
        session_id = str(uuid.uuid4())
        dm_logger.debug(f"Session ID: {session_id}")
        yield {
            "type": "user",
            "message": {"role": "user", "content": prompt},
            "parent_tool_use_id": None,
            "session_id": session_id,
        }

    try:
        async for message in query(prompt=prompt_generator(), options=options):
            process_message(message)
            yield message

        dm_logger.info("Agent query completed successfully")

    except Exception as e:
        dm_logger.error(f"Agent query failed: {e}", exc_info=True)
        raise


async def run(prompt: str) -> str:
    """
    Run agent with a prompt and return the text response.
    This is the original CLI interface (backward compatible).
    """
    responses = []
    async for message in run_query(prompt):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    responses.append(block.text)

    return "\n".join(responses)


def main():
    """CLI entry point."""
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(asyncio.run(run(prompt)))
    else:
        print("Usage: python -m dnd_dm_agent.claude_agent 'your prompt'")


if __name__ == "__main__":
    main()
