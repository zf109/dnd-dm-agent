"""DnD Dungeon Master Agent using Google ADK."""

from google.adk.agents import Agent

from config.llm_engine import create_llm_engine

from .tools.utility_tools import (
    manage_game_state,
    roll_dice,
)
from .tools.character_validation import validate_character_readiness
from .tools.character_tools import (
    manage_character_create,
    manage_character_get,
    manage_character_update,
    manage_character_add_note,
)
from .tools.session_management_tools import (
    lookup_knowledge,
    get_dnd_class_details,
    get_dm_guidance,
    list_available_knowledge,
)
from .tools.session_tools import create_game_session, list_game_sessions, add_character_to_session


# Create Claude LLM engine
claude_engine = create_llm_engine("claude-3.5-sonnet")


character_toolset = [
    validate_character_readiness,
    manage_character_create,
    manage_character_get,
    manage_character_update,
    manage_character_add_note,
]

knowledge_toolset = [
    lookup_knowledge,
    get_dnd_class_details,
    get_dm_guidance,
    list_available_knowledge,
]

utility_toolset = [
    manage_game_state,
    roll_dice,
]

session_toolset = [create_game_session, list_game_sessions, add_character_to_session]

tools = character_toolset + knowledge_toolset + session_toolset + utility_toolset

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
    - Use manage_character_create, manage_character_get, manage_character_update, and manage_character_add_note for character operations
    - When change character sheet, always use manage_character_add_note to add a timestamped note
    - When user ask you to change character, always check if it's allowed by checking the guide and knoweldge
    - Use roll_dice for any dice rolls needed during gameplay
    - Validate characters with validate_character_readiness before starting adventures  
    - Reference your knowledge base with lookup_knowledge and get_dnd_class_details for accurate D&D information
    - Log important events with log_game_event for session continuity

    Start each conversation by setting an engaging scene and asking what the players want to do.
    """,
    tools=tools,
)
