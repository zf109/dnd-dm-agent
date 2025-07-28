"""Session management and knowledge access tools for the DnD DM Agent."""

from typing import Dict, List, Any, Optional

from .knowledge_tools import (
    search_knowledge,
    get_class_information,
    get_available_knowledge,
    get_session_management_guidance,
)


def lookup_knowledge(query: str, specific_files: Optional[list] = None) -> Dict[str, Any]:
    """Search the knowledge base for information about D&D rules, classes, or session management.

    Use this tool to access detailed D&D information including class features,
    session management guidance, and other reference material.

    Args:
        query: What to search for (e.g., "Fighter", "advantage", "inspiration")
        specific_files: Optional list of files to search (e.g., ["classes_5e"])

    Returns:
        Dictionary with search results from knowledge base
    """
    try:
        return search_knowledge(query, specific_files)
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_dnd_class_details(class_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific D&D class.

    Use this tool to get comprehensive information about any D&D 5e class
    including features, abilities, and recommendations.

    Args:
        class_name: Name of the D&D class (e.g., "Fighter", "Wizard", "Rogue")

    Returns:
        Dictionary with detailed class information
    """
    try:
        return get_class_information(class_name)
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_dm_guidance(topic: Optional[str] = None) -> Dict[str, Any]:
    """Get session management and DM guidance from the knowledge base.

    Use this tool to access best practices for running D&D sessions,
    managing players, and handling various game situations.

    Args:
        topic: Optional specific topic to look up (e.g., "combat", "roleplay")

    Returns:
        Dictionary with DM guidance and best practices
    """
    try:
        return get_session_management_guidance(topic)
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def list_available_knowledge() -> Dict[str, Any]:
    """List all available knowledge files and their contents.

    Use this tool to see what knowledge is available in the system.

    Returns:
        Dictionary with available knowledge files and descriptions
    """
    try:
        return get_available_knowledge()
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
