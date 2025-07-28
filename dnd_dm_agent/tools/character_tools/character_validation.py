"""Character validation tools to ensure minimum viable character sheets."""

import re
from typing import Any, Dict
from pathlib import Path


def get_character_creation_prompts() -> Dict[str, str]:
    """Get step-by-step prompts for character creation.

    Returns:
        Dictionary of character creation prompts in order
    """
    return {
        "step_1_name": "What is your character's name?",
        "step_2_class": "What class would you like to play? (Fighter, Wizard, Rogue, Cleric, etc.)",
        "step_3_race": "What race/species is your character? (Human, Elf, Dwarf, Halfling, etc.)",
        "step_4_background": "What background does your character have? (Soldier, Noble, Criminal, Folk Hero, etc.)",
        "step_5_abilities": "Now let's determine your ability scores. Would you like to use standard array (15,14,13,12,10,8), roll dice, or point buy?",
        "step_6_equipment": "Let's select your starting equipment based on your class and background.",
        "step_7_details": "Finally, let's add some personality! What are your character's personality traits, ideals, bonds, and flaws?",
    }


def get_minimum_character_requirements() -> Dict[str, Any]:
    """Get the minimum requirements for a playable character.

    Returns:
        Dictionary defining minimum character requirements
    """
    return {
        "essential_fields": [
            "Character Name",
            "Class and Level",
            "Race/Species",
            "Background",
            "Ability Scores (all 6)",
            "Hit Points",
            "Armor Class",
        ],
        "recommended_fields": [
            "At least one weapon/attack",
            "Saving throw proficiencies",
            "Skill proficiencies",
            "Starting equipment",
            "Class features (level 1)",
            "Racial traits",
        ],
        "optional_fields": [
            "Detailed backstory",
            "Personality traits",
            "Ideals, bonds, flaws",
            "Specific equipment details",
            "Spell lists (for casters)",
            "Physical description",
        ],
    }


def tool_validate_character_readiness(session_name: str, character_name: str) -> Dict[str, Any]:
    """Validate that a character has minimum required information to start gameplay.

    Args:
        session_name: Name of the game session
        character_name: Name of the character to validate

    Returns:
        Dictionary with validation results and missing fields
    """
    # Import here to avoid circular imports
    from .character_tools import load_character_data

    character = load_character_data(session_name, character_name)
    if not character:
        return {
            "status": "not_found",
            "message": f"Character '{character_name}' not found in session '{session_name}'",
            "missing_fields": ["Character not found"],
            "warnings": [],
            "total_missing": 1,
        }

    missing_fields = []
    warnings = []

    # Check basic info
    basic_info = character.get("basic_info", {})
    if not basic_info.get("name"):
        missing_fields.append("Character Name")
    if not basic_info.get("class") or not basic_info.get("level"):
        missing_fields.append("Class and Level")
    if not basic_info.get("race"):
        missing_fields.append("Race/Species")
    if not basic_info.get("background"):
        missing_fields.append("Background")

    # Check ability scores
    ability_scores = character.get("ability_scores", {})
    abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    missing_abilities = []
    for ability in abilities:
        if ability not in ability_scores or not ability_scores[ability].get("score"):
            missing_abilities.append(ability.capitalize())

    if missing_abilities:
        missing_fields.append(f"Ability Scores ({', '.join(missing_abilities)})")

    # Check combat stats
    combat_stats = character.get("combat_stats", {})
    if not combat_stats.get("armor_class"):
        missing_fields.append("Armor Class")

    hit_points = combat_stats.get("hit_points", {})
    if not hit_points.get("maximum") or not hit_points.get("current"):
        missing_fields.append("Hit Points")

    # Check for at least one attack/weapon
    attacks = character.get("attacks", [])
    equipment = character.get("equipment", {})
    weapons = equipment.get("weapons", [])

    if not attacks and not weapons:
        warnings.append("No weapons or attacks defined - character should have at least one attack option")

    # Determine readiness level
    if not missing_fields:
        status = "ready"
        message = "Character is ready for gameplay!"
    elif len(missing_fields) <= 2:
        status = "mostly_ready"
        message = f"Character is mostly ready, but missing: {', '.join(missing_fields)}"
    else:
        status = "not_ready"
        message = "Character needs more information before gameplay can begin"

    return {
        "status": status,
        "message": message,
        "missing_fields": missing_fields,
        "warnings": warnings,
        "total_missing": len(missing_fields),
    }
