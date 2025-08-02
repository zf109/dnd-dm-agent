"""DnD Dungeon Master Agent using Google ADK."""

from google.adk.agents import Agent

from config.llm_engine import create_llm_engine

from .tools.utility_tools import (
    manage_game_state,
    roll_dice,
)
from .tools.character_tools import (
    tool_create_character,
    tool_get_character,
    tool_update_character,
    tool_add_character_note,
    tool_validate_character_readiness,
)
from .tools.knowledge_tools import (
    lookup_knowledge,
    get_dnd_class_details,
    get_spell_details,
    get_monster_details,
    get_dm_guidance,
    list_available_knowledge,
)
from .tools.session_tools import (
    create_game_session,
    list_game_sessions,
    add_character_to_session,
    update_session_log,
    get_session_log,
)
from .tools.campaign_tools import (
    list_campaigns,
    load_campaign,
)

# Create Claude LLM engine
claude_engine = create_llm_engine("claude-3.5-sonnet")


character_toolset = [
    tool_validate_character_readiness,
    tool_create_character,
    tool_get_character,
    tool_update_character,
    tool_add_character_note,
]

knowledge_toolset = [
    lookup_knowledge,
    get_dnd_class_details,
    get_spell_details,
    get_monster_details,
    get_dm_guidance,
    list_available_knowledge,
]

utility_toolset = [
    manage_game_state,
    roll_dice,
]

session_toolset = [create_game_session, list_game_sessions, add_character_to_session, update_session_log, get_session_log]

campaign_toolset = [list_campaigns, load_campaign]

tools = character_toolset + knowledge_toolset + session_toolset + campaign_toolset + utility_toolset

# The main DM agent
root_agent = Agent(
    name="dungeon_master",
    model=claude_engine.create_model(),
    description="An experienced Dungeon Master for D&D adventures",
    instruction="""
    You are an experienced Dungeon Master for Dungeons & Dragons. 

    For detailed guidance on how to run sessions, manage characters, and use your tools effectively, 
    use get_dm_guidance() to access your comprehensive session management guide.

    Key reminders:
    - Always create a game session before character creation using create_game_session
    - Use tool_create_character, tool_get_character, tool_update_character, and tool_add_character_note for character operations
    - When change character sheet, always use tool_add_character_note to add a timestamped note
    - When user ask you to change character, always check if it's allowed by checking the guide and knoweldge
    - Use roll_dice for any dice rolls needed during gameplay
    - Validate characters with tool_validate_character_readiness before starting adventures  
    - Reference your knowledge base with lookup_knowledge and get_dnd_class_details for accurate D&D information
    - Use list_campaigns and load_campaign to access pre-made campaign skeletons for structured adventures
    - Use get_session_log to read previous session history for continuity
    - Use manage_game_state(session_name, action, location, scene) to track current location and scene
    - ALWAYS log location/scene changes with update_session_log immediately after using manage_game_state
    - When starting a conversation, check previous session logs for continuity and reference recent events
    - Log important events with update_session_log for session continuity

    Start each conversation by setting an engaging scene and asking what the players want to do.
    """,
    tools=tools,
)
