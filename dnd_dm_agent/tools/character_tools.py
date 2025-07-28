"""Character sheet management tools for D&D 5e game sessions."""

import json
import os
import collections.abc
from pathlib import Path
from copy import deepcopy
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from .character_schema import get_default_character_template, calculate_modifier, calculate_proficiency_bonus
from .session_tools import SESSIONS_DIR
from ..utils.logger import get_logger

logger = get_logger(__name__)


def manage_character_create(
    session_name: str,
    character_name: str,
    character_class: Optional[str] = None,
    race: Optional[str] = None,
    background: Optional[str] = None,
    alignment: Optional[str] = None,
    level: int = 1,
    strength: int = 15,
    dexterity: int = 14,
    constitution: int = 13,
    intelligence: int = 12,
    wisdom: int = 10,
    charisma: int = 8,
    hit_points_max: int = 10,
    armor_class: int = 15,
) -> Optional[Dict[str, Any]]:
    """Create a new character.

    Args:
        session_name: Name of the game session
        character_name: Name of the character
        character_class: Character class (defaults to "Fighter")
        race: Character race (defaults to "Human")
        background: Character background (defaults to "Soldier")
        alignment: Character alignment (defaults to "Neutral")
        level: Character level (defaults to 1)
        strength: Strength ability score (defaults to 15)
        dexterity: Dexterity ability score (defaults to 14)
        constitution: Constitution ability score (defaults to 13)
        intelligence: Intelligence ability score (defaults to 12)
        wisdom: Wisdom ability score (defaults to 10)
        charisma: Charisma ability score (defaults to 8)
        hit_points_max: Maximum hit points (defaults to 10)
        armor_class: Armor class (defaults to 15)

    Returns:
        Character data dictionary on success, None on failure
    """
    logger.info(f"Creating character '{character_name}' in session '{session_name}'")
    logger.debug(f"Creating character with class='{character_class}', race='{race}', level={level}")

    # Use pure function to create character data
    character_data = create_character_data(
        character_name=character_name,
        character_class=character_class,
        race=race,
        background=background,
        alignment=alignment,
        level=level,
        strength=strength,
        dexterity=dexterity,
        constitution=constitution,
        intelligence=intelligence,
        wisdom=wisdom,
        charisma=charisma,
        hit_points_max=hit_points_max,
        armor_class=armor_class,
    )
    logger.debug(f"Character data created with keys: {list(character_data.keys())}")

    # Handle I/O: save the character
    success = save_character_data(session_name, character_name, character_data, session_dir=SESSIONS_DIR)
    logger.info(f"Character save result: {success}")
    return character_data if success else None


def manage_character_get(
    session_name: str,
    character_name: str,
) -> Optional[Dict[str, Any]]:
    """Get an existing character.

    Args:
        session_name: Name of the game session
        character_name: Name of the character

    Returns:
        Character data dictionary on success, None if not found
    """
    logger.info(f"Getting character '{character_name}' from session '{session_name}'")
    # Handle I/O: load the character
    character_data = load_character_data(session_name, character_name, session_dir=SESSIONS_DIR)
    logger.info(f"Character found: {character_data is not None}")
    return character_data


def manage_character_update(
    session_name: str,
    character_name: str,
    updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Update an existing character.

    Args:
        session_name: Name of the game session
        character_name: Name of the character
        updates: Dictionary of fields to update

    Returns:
        Updated character data dictionary on success, None on failure
    """
    logger.info(f"Updating character '{character_name}' in session '{session_name}' with updates: {updates}")

    # Handle I/O: load existing character
    existing_character = load_character_data(session_name, character_name, session_dir=SESSIONS_DIR)
    if not existing_character:
        logger.warning(f"Character '{character_name}' not found for update")
        return None

    logger.debug(f"Loaded existing character with keys: {list(existing_character.keys())}")

    # Use pure function to update character data
    updated_character = update_character_data(existing_character, updates)
    logger.debug(f"Updated character data prepared")

    # Handle I/O: save updated character
    success = save_character_data(session_name, character_name, updated_character, session_dir=SESSIONS_DIR)
    logger.info(f"Character update save result: {success}")
    return updated_character if success else None


def manage_character_add_note(
    session_name: str,
    character_name: str,
    note: str,
) -> Optional[Dict[str, Any]]:
    """Add a note to an existing character.

    Args:
        session_name: Name of the game session
        character_name: Name of the character
        note: The note text to add

    Returns:
        Updated character data dictionary on success, None on failure
    """
    logger.info(
        f"Adding note to character '{character_name}' in session '{session_name}': {note[:50]}{'...' if len(note) > 50 else ''}"
    )

    # Handle I/O: load existing character
    existing_character = load_character_data(session_name, character_name, session_dir=SESSIONS_DIR)
    if not existing_character:
        logger.warning(f"Character '{character_name}' not found for adding note")
        return None

    # Use pure function to add note
    updated_character = add_character_note_data(existing_character, note, session_name)

    # Handle I/O: save updated character
    success = save_character_data(session_name, character_name, updated_character, session_dir=SESSIONS_DIR)
    logger.info(f"Character note save result: {success}")
    return updated_character if success else None


def create_character_data(
    character_name: str,
    character_class: str = None,
    race: str = None,
    background: str = None,
    alignment: str = None,
    level: int = 1,
    **kwargs,
) -> Dict[str, Any]:
    """Create a new character data dictionary (pure function, no I/O).

    Args:
        character_name: Name of the character
        character_class: Character class (defaults to Fighter)
        race: Character race (defaults to Human)
        background: Character background (defaults to Soldier)
        alignment: Character alignment (defaults to Neutral)
        level: Character level (defaults to 1)
        **kwargs: Additional character attributes (strength, dexterity, etc.)

    Returns:
        Complete character data dictionary
    """
    # Start with complete character template
    character = get_default_character_template()

    # Fill in provided data
    character["basic_info"]["name"] = character_name
    character["basic_info"]["class"] = character_class or "Fighter"
    character["basic_info"]["level"] = level
    character["basic_info"]["race"] = race or "Human"
    character["basic_info"]["background"] = background or "Soldier"
    character["basic_info"]["alignment"] = alignment or "Neutral"

    # Set ability scores and calculate derived values
    str_score = kwargs.get("strength", 15)
    dex_score = kwargs.get("dexterity", 14)
    con_score = kwargs.get("constitution", 13)
    int_score = kwargs.get("intelligence", 12)
    wis_score = kwargs.get("wisdom", 10)
    cha_score = kwargs.get("charisma", 8)

    # Update ability scores with modifiers
    for ability, score in [
        ("strength", str_score),
        ("dexterity", dex_score),
        ("constitution", con_score),
        ("intelligence", int_score),
        ("wisdom", wis_score),
        ("charisma", cha_score),
    ]:
        modifier = calculate_modifier(score)
        character["ability_scores"][ability]["score"] = score
        character["ability_scores"][ability]["modifier"] = modifier
        character["ability_scores"][ability]["saving_throw"] = modifier

    # Update combat stats
    character["proficiency_bonus"] = calculate_proficiency_bonus(level)
    character["combat_stats"]["hit_points"]["current"] = kwargs.get("hit_points_max", 10)
    character["combat_stats"]["hit_points"]["maximum"] = kwargs.get("hit_points_max", 10)
    character["combat_stats"]["armor_class"] = kwargs.get("armor_class", 15)
    character["combat_stats"]["initiative"] = calculate_modifier(dex_score)
    character["combat_stats"]["hit_dice"]["available"] = level
    character["combat_stats"]["hit_dice"]["total"] = level

    # Update skill modifiers based on ability scores
    for skill, skill_data in character["skills"].items():
        ability = skill_data["ability"]
        ability_mod = character["ability_scores"][ability]["modifier"]
        skill_data["modifier"] = ability_mod

    return character


def _get_characters_dir(session_name: str, session_dir: Optional[str] = None) -> Path:
    if not session_dir:
        return Path("game_sessions") / session_name / "characters"
    else:
        return Path(session_dir) / session_name / "characters"


def load_character_data(
    session_name: str, character_name: str, session_dir: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Load complete character data from session."""
    characters_dir = _get_characters_dir(session_name=session_name, session_dir=session_dir)
    logger.debug(f"Loading character from directory: {characters_dir}")

    # Create sanitized filename
    character_filename = character_name.lower().replace(" ", "_")
    filepath = characters_dir / f"{character_filename}.json"
    logger.debug(f"Loading character from file: {filepath}")

    if not filepath.exists():
        logger.warning(f"Character file does not exist: {filepath}")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            character_data = json.load(f)
            logger.debug(f"Successfully loaded character data with {len(character_data)} top-level keys")
            return character_data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load character data from {filepath}: {e}")
        return None


def save_character_data(
    session_name: str, character_name: str, character_data: Dict[str, Any], session_dir: Optional[str] = None
) -> bool:
    """Save complete character data to session."""

    characters_dir = _get_characters_dir(session_name=session_name, session_dir=session_dir)
    logger.debug(f"Saving character to directory: {characters_dir}")

    # Ensure directories exist
    characters_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created/verified directory exists: {characters_dir}")

    # Create sanitized filename
    character_filename = character_name.lower().replace(" ", "_")
    filepath = characters_dir / f"{character_filename}.json"
    logger.debug(f"Saving character to file: {filepath}")

    # Update last modified timestamp
    if "metadata" not in character_data:
        character_data["metadata"] = {}
    character_data["metadata"]["last_updated"] = datetime.now().isoformat()

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(character_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved character data to {filepath}")
        logger.debug(f"File size after save: {filepath.stat().st_size if filepath.exists() else 'file not found'}")
        return True
    except (IOError, TypeError) as e:
        logger.error(f"Failed to save character data to {filepath}: {e}")
        return False


def deep_update_dict(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """Recursively update nested dictionary in place using collections.abc.Mapping.

    Args:
        base_dict: Dictionary to update (modified in place)
        update_dict: Dictionary containing updates to apply
    """
    logger.debug(f"Deep updating with {len(update_dict)} keys: {list(update_dict.keys())}")
    for k, v in update_dict.items():
        if isinstance(v, collections.abc.Mapping):
            logger.debug(f"Recursively updating nested key '{k}' with {len(v)} sub-keys")
            base_dict[k] = deep_update_dict(base_dict.get(k, {}), v)
        else:
            logger.debug(f"Setting key '{k}' = {v}")
            base_dict[k] = v
    return base_dict


def update_character_data(character_data: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update character data with given attributes (pure function, no I/O).

    Args:
        character_data: Existing character data dictionary
        updates: Dictionary of updates to apply to the character

    Returns:
        Updated character data dictionary
    """
    logger.debug(f"Updating character data with {len(updates)} update sections")
    logger.debug(f"Update keys: {list(updates.keys())}")

    # Create a copy to avoid mutating the original
    character = deepcopy(character_data)
    logger.debug(f"Created deep copy of character data")

    # Apply updates to the copy
    deep_update_dict(character, updates)
    logger.debug(f"Applied deep updates to character copy")
    return character


def add_character_note_data(character_data: Dict[str, Any], note: str, session_name: str) -> Dict[str, Any]:
    """Add note to character data (pure function, no I/O).

    Args:
        character_data: Existing character data dictionary
        note: The note text to add
        session_name: Session name to organize notes by

    Returns:
        Updated character data dictionary with added note
    """
    # Create a copy to avoid mutating the original
    character = deepcopy(character_data) if character_data else {}

    # Initialize notes structure if it doesn't exist
    if "notes" not in character:
        character["notes"] = {}

    # Initialize session notes list if it doesn't exist
    if session_name not in character["notes"]:
        character["notes"][session_name] = []

    # Add the note with timestamp
    timestamped_note = {"note": note, "timestamp": datetime.now().isoformat()}

    character["notes"][session_name].append(timestamped_note)
    return character
