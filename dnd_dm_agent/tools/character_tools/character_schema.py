"""Character sheet schema and template for D&D 5e characters."""

from typing import Dict, Any
from datetime import datetime


def get_default_character_template() -> Dict[str, Any]:
    """Return a complete character template with all fields from the markdown template."""
    return {
        "basic_info": {
            "name": "",
            "class": "",
            "level": 1,
            "race": "",
            "background": "",
            "alignment": "",
            "experience_points": 0,
        },
        "ability_scores": {
            "strength": {"score": 10, "modifier": 0, "saving_throw": 0, "proficient": False},
            "dexterity": {"score": 10, "modifier": 0, "saving_throw": 0, "proficient": False},
            "constitution": {"score": 10, "modifier": 0, "saving_throw": 0, "proficient": False},
            "intelligence": {"score": 10, "modifier": 0, "saving_throw": 0, "proficient": False},
            "wisdom": {"score": 10, "modifier": 0, "saving_throw": 0, "proficient": False},
            "charisma": {"score": 10, "modifier": 0, "saving_throw": 0, "proficient": False},
        },
        "proficiency_bonus": 2,
        "combat_stats": {
            "armor_class": 10,
            "hit_points": {"current": 10, "maximum": 10, "temporary": 0},
            "hit_dice": {"available": 1, "total": 1},
            "speed": 30,
            "initiative": 0,
        },
        "death_saves": {"successes": 0, "failures": 0},
        "skills": {
            "athletics": {"proficient": False, "modifier": 0, "ability": "strength"},
            "acrobatics": {"proficient": False, "modifier": 0, "ability": "dexterity"},
            "sleight_of_hand": {"proficient": False, "modifier": 0, "ability": "dexterity"},
            "stealth": {"proficient": False, "modifier": 0, "ability": "dexterity"},
            "arcana": {"proficient": False, "modifier": 0, "ability": "intelligence"},
            "history": {"proficient": False, "modifier": 0, "ability": "intelligence"},
            "investigation": {"proficient": False, "modifier": 0, "ability": "intelligence"},
            "nature": {"proficient": False, "modifier": 0, "ability": "intelligence"},
            "religion": {"proficient": False, "modifier": 0, "ability": "intelligence"},
            "animal_handling": {"proficient": False, "modifier": 0, "ability": "wisdom"},
            "insight": {"proficient": False, "modifier": 0, "ability": "wisdom"},
            "medicine": {"proficient": False, "modifier": 0, "ability": "wisdom"},
            "perception": {"proficient": False, "modifier": 0, "ability": "wisdom"},
            "survival": {"proficient": False, "modifier": 0, "ability": "wisdom"},
            "deception": {"proficient": False, "modifier": 0, "ability": "charisma"},
            "intimidation": {"proficient": False, "modifier": 0, "ability": "charisma"},
            "performance": {"proficient": False, "modifier": 0, "ability": "charisma"},
            "persuasion": {"proficient": False, "modifier": 0, "ability": "charisma"},
        },
        "proficiencies": {"armor": [], "weapons": [], "tools": [], "languages": ["Common"]},
        "attacks": [],
        "equipment": {"currency": {"cp": 0, "sp": 0, "gp": 0, "pp": 0}, "armor": [], "weapons": [], "gear": []},
        "features_and_traits": {"racial_traits": [], "class_features": [], "background_features": []},
        "spellcasting": {
            "ability": None,
            "spell_save_dc": None,
            "spell_attack_bonus": None,
            "spell_slots": {
                "cantrips": 0,
                "level_1": 0,
                "level_2": 0,
                "level_3": 0,
                "level_4": 0,
                "level_5": 0,
                "level_6": 0,
                "level_7": 0,
                "level_8": 0,
                "level_9": 0,
            },
            "spells_known": {
                "cantrips": [],
                "level_1": [],
                "level_2": [],
                "level_3": [],
                "level_4": [],
                "level_5": [],
                "level_6": [],
                "level_7": [],
                "level_8": [],
                "level_9": [],
            },
        },
        "character_details": {"personality_traits": [], "ideals": [], "bonds": [], "flaws": [], "backstory": ""},
        "notes": {},
        "advancement": {"ability_score_improvements": [], "multiclassing": []},
        "metadata": {
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "version": "1.0",
        },
    }


def calculate_modifier(ability_score: int) -> int:
    """Calculate ability modifier from ability score."""
    return (ability_score - 10) // 2


def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on character level."""
    if level <= 4:
        return 2
    elif level <= 8:
        return 3
    elif level <= 12:
        return 4
    elif level <= 16:
        return 5
    else:
        return 6
