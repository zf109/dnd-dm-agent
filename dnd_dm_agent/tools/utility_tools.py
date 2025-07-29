"""Utility tools for DnD DM Agent - dice rolling, game state, and convenience functions."""

import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from .session_tools import SESSIONS_DIR



def parse_dice_notation(notation: str) -> tuple[int, int, int]:
    """Parse dice notation like '2d6+3' into (count, sides, modifier)."""
    notation = notation.strip().lower().replace(" ", "")

    # Match patterns like 1d20, 2d6+3, 3d8-1, d20 (implicit 1)
    pattern = r"^(\d*)d(\d+)([+-]\d+)?$"
    match = re.match(pattern, notation)

    if not match:
        raise ValueError(f"Invalid dice notation: {notation}")

    count_str, sides_str, modifier_str = match.groups()

    count = int(count_str) if count_str else 1
    sides = int(sides_str)
    modifier = int(modifier_str) if modifier_str else 0

    return count, sides, modifier


def roll_dice(notation: str) -> Dict[str, Any]:
    """Roll dice using standard DnD notation (e.g., '1d20+5', '2d6').

    Use this tool whenever you need to roll dice for ability checks, attacks,
    damage, saving throws, or any other game mechanic that requires randomness.

    Args:
        notation: Dice notation like '1d20+3', '2d6', or '4d6+2'

    Returns:
        A dictionary containing the roll results with status, individual rolls,
        total, and notation used.
    """
    try:
        count, sides, modifier = parse_dice_notation(notation)
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + modifier
        result = {"dice_notation": notation, "individual_rolls": rolls, "total": total, "modifier": modifier}
        return {
            "status": "success",
            "notation": result["dice_notation"],
            "individual_rolls": result["individual_rolls"],
            "total": result["total"],
            "modifier": result["modifier"],
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def manage_game_state(session_name: str, action: str, location: Optional[str] = None, scene: Optional[str] = None) -> Dict[str, Any]:
    """Get or update game state information for a specific session.

    Use this tool to track the current game state, update locations,
    or modify the current scene description. Changes are automatically
    saved to session metadata.

    Args:
        session_name: Name of the game session
        action: Action to perform - 'get_state', 'update_location', or 'update_scene'
        location: New location name (only for update_location action)
        scene: New scene description (only for update_scene action)

    Returns:
        Dictionary with current game state or update confirmation
    """
    try:
        session_path = SESSIONS_DIR / session_name
        if not session_path.exists():
            return {"status": "error", "error_message": f"Session '{session_name}' does not exist"}

        metadata_path = session_path / "session_metadata.json" 
        
        # Load current metadata
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        if action == "get_state":
            return {
                "status": "success",
                "current_location": metadata.get("current_location", "Unknown Location"),
                "current_scene": metadata.get("current_scene", ""),
                "characters": metadata.get("characters", []),
                "session_name": session_name,
            }
        elif action == "update_location" and location:
            metadata["current_location"] = location
            metadata["last_played"] = datetime.now().isoformat()
            
            # Save metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            return {"status": "success", "location": location}
        elif action == "update_scene" and scene:
            metadata["current_scene"] = scene
            metadata["last_played"] = datetime.now().isoformat()
            
            # Save metadata
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            return {"status": "success", "scene": scene}
        else:
            return {"status": "error", "error_message": "Invalid action or missing required parameters"}
    except Exception as e:
        return {"status": "error", "error_message": str(e)}
