"""Knowledge access tools for the DnD DM Agent."""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def get_knowledge_files() -> Dict[str, Path]:
    """Get all available knowledge files.

    Returns:
        Dictionary mapping knowledge file names to their paths
    """
    knowledge_dir = Path(__file__).parent.parent / "knowledge"

    knowledge_files = {}
    if knowledge_dir.exists():
        for file_path in knowledge_dir.glob("**/*.md"):
            # Use relative path from knowledge dir as key for nested structure
            relative_path = file_path.relative_to(knowledge_dir)
            # Convert path to key: "spells/level_1_spells" instead of just "level_1_spells"
            key = str(relative_path.with_suffix(''))
            knowledge_files[key] = file_path

    return knowledge_files


def load_knowledge_file(filename: str) -> Dict[str, Any]:
    """Load a specific knowledge file.

    Args:
        filename: Name of the knowledge file (without .md extension)

    Returns:
        Dictionary with file content or error
    """
    try:
        knowledge_files = get_knowledge_files()

        if filename not in knowledge_files:
            available = list(knowledge_files.keys())
            return {
                "status": "error",
                "error_message": f"Knowledge file '{filename}' not found. Available files: {available}",
            }

        file_path = knowledge_files[filename]
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {"status": "success", "filename": filename, "content": content, "file_path": str(file_path)}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to load knowledge file: {str(e)}"}


def lookup_knowledge(query: str, specific_files: Optional[List[str]] = None) -> Dict[str, Any]:
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
        knowledge_files = get_knowledge_files()

        if specific_files:
            # Search only specified files
            search_files = {name: path for name, path in knowledge_files.items() if name in specific_files}
        else:
            # Search all files
            search_files = knowledge_files

        results = []

        for filename, file_path in search_files.items():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find sections containing the query
                sections = _extract_matching_sections(content, query)

                if sections:
                    results.append({"file": filename, "sections": sections})

            except Exception as e:
                continue  # Skip files that can't be read

        return {"status": "success", "query": query, "results": results, "files_searched": list(search_files.keys())}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to search knowledge: {str(e)}"}


def _extract_matching_sections(content: str, query: str) -> List[Dict[str, str]]:
    """Extract sections from markdown content that match the query using regex.

    Args:
        content: Markdown content to search
        query: Search query (supports basic regex patterns)

    Returns:
        List of matching sections with headers and content
    """
    sections = []
    lines = content.split("\n")
    current_section = None
    current_content = []
    
    # Compile regex pattern (case insensitive)
    try:
        pattern = re.compile(query, re.IGNORECASE)
    except re.error:
        # If regex is invalid, escape it and search as literal string
        pattern = re.compile(re.escape(query), re.IGNORECASE)

    for line in lines:
        # Check if this is a header line
        if line.startswith("#"):
            # Save previous section if it matched
            if current_section and current_content:
                section_text = "\n".join(current_content)
                if pattern.search(section_text) or pattern.search(current_section):
                    sections.append({"header": current_section, "content": "\n".join(current_content).strip()})

            # Start new section
            current_section = line
            current_content = []
        else:
            current_content.append(line)

    # Check final section
    if current_section and current_content:
        section_text = "\n".join(current_content)
        if pattern.search(section_text) or pattern.search(current_section):
            sections.append({"header": current_section, "content": "\n".join(current_content).strip()})

    return sections


def get_dnd_class_details(class_name: str) -> Dict[str, Any]:
    """Get detailed information about a D&D class from the classes_5e knowledge file.

    Args:
        class_name: Name of the D&D class

    Returns:
        Dictionary with class information
    """
    try:
        # Load the classes knowledge file
        result = load_knowledge_file("classes_5e")
        if result["status"] != "success":
            return result

        content = result["content"]

        # Search for the specific class
        search_result = _extract_matching_sections(content, class_name.lower())

        if not search_result:
            return {"status": "error", "error_message": f"Class '{class_name}' not found in knowledge base"}

        return {"status": "success", "class_name": class_name, "information": search_result}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to get class information: {str(e)}"}


def list_available_knowledge() -> Dict[str, Any]:
    """List all available knowledge files and their descriptions.

    Returns:
        Dictionary with available knowledge files
        
    Note:
        Descriptions are truncated to first 200 characters with "..." appended
    """
    try:
        knowledge_files = get_knowledge_files()

        file_info = {}
        for filename, file_path in knowledge_files.items():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    # Read first few lines to get description
                    lines = f.readlines()[:10]
                    description = "".join(lines).strip()[:200] + "..."

                file_info[filename] = {"path": str(file_path), "description": description}
            except:
                file_info[filename] = {"path": str(file_path), "description": "Could not read file"}

        return {"status": "success", "available_files": file_info, "total_files": len(knowledge_files)}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to get available knowledge: {str(e)}"}


def get_spell_details(spell_name: str) -> Dict[str, Any]:
    """Get detailed information about a D&D spell from spell knowledge files.

    Args:
        spell_name: Name of the spell (e.g., "Fire Bolt", "Magic Missile")

    Returns:
        Dictionary with spell information
    """
    try:
        knowledge_files = get_knowledge_files()
        
        # Filter to only spell files
        spell_files = {name: path for name, path in knowledge_files.items() 
                      if name.startswith("player_handbook/spells/")}
        
        if not spell_files:
            return {"status": "error", "error_message": "No spell files found in knowledge base"}

        # Search across all spell files
        for filename, file_path in spell_files.items():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Search for the specific spell
                search_result = _extract_matching_sections(content, spell_name)

                if search_result:
                    return {"status": "success", "spell_name": spell_name, "information": search_result}
            except Exception:
                continue  # Skip files that can't be read

        return {"status": "error", "error_message": f"Spell '{spell_name}' not found in knowledge base"}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to get spell information: {str(e)}"}


def get_monster_details(monster_name: str) -> Dict[str, Any]:
    """Get detailed information about a D&D monster from monster knowledge files.

    Args:
        monster_name: Name of the monster (e.g., "Goblin", "Red Dragon", "Owlbear")

    Returns:
        Dictionary with monster information
    """
    try:
        knowledge_files = get_knowledge_files()
        
        # Filter to only monster files
        monster_files = {name: path for name, path in knowledge_files.items() 
                        if name.startswith("monster_manual/")}
        
        if not monster_files:
            return {"status": "error", "error_message": "No monster files found in knowledge base"}

        # Search across all monster files
        for filename, file_path in monster_files.items():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Search for the specific monster
                search_result = _extract_matching_sections(content, monster_name)

                if search_result:
                    return {"status": "success", "monster_name": monster_name, "information": search_result}
            except Exception:
                continue  # Skip files that can't be read

        return {"status": "error", "error_message": f"Monster '{monster_name}' not found in knowledge base"}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to get monster information: {str(e)}"}


def get_dm_guidance(topic: Optional[str] = None) -> Dict[str, Any]:
    """Get session management guidance from the session_management_guide knowledge file.

    Args:
        topic: Optional specific topic to search for

    Returns:
        Dictionary with session management information
    """
    try:
        result = load_knowledge_file("session_management_guide")
        if result["status"] != "success":
            return result

        content = result["content"]

        if topic:
            # Search for specific topic
            sections = _extract_matching_sections(content, topic.lower())
            if sections:
                return {"status": "success", "topic": topic, "guidance": sections}
            else:
                return {"status": "error", "error_message": f"Topic '{topic}' not found in session management guide"}
        else:
            # Return full guide
            return {"status": "success", "content": content}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to get session management guidance: {str(e)}"}


