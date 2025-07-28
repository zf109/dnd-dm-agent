"""Session management tools for DnD DM Agent."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Base directory for game sessions
SESSIONS_DIR = Path(__file__).parent.parent / "game_sessions"


def create_game_session(session_name: str, dm_name: str = "DM") -> Dict[str, Any]:
    """Create a new game session with its own folder and metadata.

    Args:
        session_name: Name of the game session
        dm_name: Name of the Dungeon Master

    Returns:
        Dictionary with session creation status and details
    """
    try:
        # Create sessions directory if it doesn't exist
        SESSIONS_DIR.mkdir(exist_ok=True)

        # Create session folder
        session_path = SESSIONS_DIR / session_name
        session_path.mkdir(exist_ok=True)

        # Create characters subfolder
        characters_path = session_path / "characters"
        characters_path.mkdir(exist_ok=True)

        # Create session metadata
        metadata = {
            "session_name": session_name,
            "dm_name": dm_name,
            "created_date": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "characters": [],
            "session_notes": "",
            "current_location": "Starting Location",
            "current_scene": "The adventure begins...",
        }

        # Save metadata
        metadata_path = session_path / "session_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Create session log
        log_path = session_path / "session_log.md"
        with open(log_path, "w") as f:
            f.write(f"# {session_name} - Session Log\n\n")
            f.write(f"**DM:** {dm_name}\n")
            f.write(f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("## Session History\n\n")
            f.write("### Session 1\n")
            f.write(f"*{datetime.now().strftime('%Y-%m-%d')}*\n\n")
            f.write("- Game session created\n")
            f.write("- Ready for character creation\n\n")

        return {
            "status": "success",
            "message": f"Game session '{session_name}' created successfully!",
            "session_path": str(session_path),
            "metadata": metadata,
        }

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to create session: {str(e)}"}


def list_game_sessions() -> Dict[str, Any]:
    """List all available game sessions.

    Returns:
        Dictionary with list of available sessions
    """
    try:
        if not SESSIONS_DIR.exists():
            return {
                "status": "success",
                "sessions": [],
                "message": "No game sessions found. Create a new session to get started!",
            }

        sessions = []
        for session_dir in SESSIONS_DIR.iterdir():
            if session_dir.is_dir():
                metadata_path = session_dir / "session_metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, "r") as f:
                            metadata = json.load(f)
                        sessions.append(
                            {
                                "name": metadata.get("session_name", session_dir.name),
                                "dm": metadata.get("dm_name", "Unknown"),
                                "created": metadata.get("created_date", "Unknown"),
                                "last_played": metadata.get("last_played", "Unknown"),
                                "character_count": len(metadata.get("characters", [])),
                            }
                        )
                    except:
                        # If metadata is corrupted, still show the session
                        sessions.append(
                            {
                                "name": session_dir.name,
                                "dm": "Unknown",
                                "created": "Unknown",
                                "last_played": "Unknown",
                                "character_count": 0,
                            }
                        )

        return {"status": "success", "sessions": sessions, "count": len(sessions)}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to list sessions: {str(e)}"}


def update_session_log(session_name: str, log_entry: str) -> Dict[str, Any]:
    """Add an entry to the session log.

    Args:
        session_name: Name of the game session
        log_entry: Text to add to the session log

    Returns:
        Dictionary with update status
    """
    try:
        session_path = SESSIONS_DIR / session_name
        if not session_path.exists():
            return {"status": "error", "error_message": f"Session '{session_name}' does not exist"}

        log_path = session_path / "session_log.md"
        timestamp = datetime.now().strftime("%H:%M")

        with open(log_path, "a") as f:
            f.write(f"- [{timestamp}] {log_entry}\n")

        # Update last played in metadata
        metadata_path = session_path / "session_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            metadata["last_played"] = datetime.now().isoformat()
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

        return {"status": "success", "message": "Session log updated successfully"}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to update session log: {str(e)}"}


def add_character_to_session(session_name: str, character_name: str) -> Dict[str, Any]:
    """Add a character to the session metadata.

    Args:
        session_name: Name of the game session
        character_name: Name of the character to add

    Returns:
        Dictionary with update status
    """
    try:
        session_path = SESSIONS_DIR / session_name
        if not session_path.exists():
            return {"status": "error", "error_message": f"Session '{session_name}' does not exist"}

        # Update session metadata
        metadata_path = session_path / "session_metadata.json"
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Add character to metadata if not already present
        if character_name not in metadata["characters"]:
            metadata["characters"].append(character_name)
            metadata["last_played"] = datetime.now().isoformat()

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Update session log
            log_path = session_path / "session_log.md"
            with open(log_path, "a") as f:
                f.write(f"- Character '{character_name}' joined the session\n")

            return {"status": "success", "message": f"Character '{character_name}' added to session"}
        else:
            return {"status": "success", "message": f"Character '{character_name}' already in session"}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to add character to session: {str(e)}"}
