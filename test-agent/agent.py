"""Simple test agent using Google ADK."""

from typing import Optional, Dict, Any

from google.adk.agents import Agent

from config.llm_engine import create_llm_engine


def say_hello(name: str = "there") -> str:
    """Say hello to someone.

    Args:
        name: The name of the person to greet

    Returns:
        A greeting message
    """
    return f"Hello, {name}! How can I help you today (this is from a script)?"


def create_char(name: str, character_data: Dict[str, Any], **kwargs) -> str:
    """Create a character with character data given.

    Args:
        character_data: Existing character data dictionary
        updates: Dictionary of updates to apply to the character

    Returns:
        Updated character data dictionary
    """
    character_data["name"] = name
    if "staff" in kwargs:
        character_data["wizard"] = "rules"
    for key, value in kwargs.items():
        character_data[key] = value
    return character_data


# Create Claude LLM engine
claude_engine = create_llm_engine("claude-3.5-sonnet")
# Create the test agent
root_agent = Agent(
    name="test_assistant",
    model=claude_engine.create_model(),
    description="A simple test assistant that can greet users",
    instruction="""
    You are a helpful and friendly assistant. Your main job is to greet users and provide basic assistance.
    
    When someone asks you to greet them or say hello, use the say_hello tool.
    Be polite, helpful, and engaging in your responses.

    When someone asks you to create a character, use the create_char tool, any play back the value returned by the tool.
    """,
    tools=[say_hello, create_char],
)
