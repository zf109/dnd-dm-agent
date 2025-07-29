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
        for file_path in knowledge_dir.glob("*.md"):
            knowledge_files[file_path.stem] = file_path

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


def search_knowledge(query: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """Search across knowledge files for information.

    Args:
        query: Search term or question
        files: Optional list of specific files to search (defaults to all)

    Returns:
        Dictionary with search results
    """
    try:
        knowledge_files = get_knowledge_files()

        if files:
            # Search only specified files
            search_files = {name: path for name, path in knowledge_files.items() if name in files}
        else:
            # Search all files
            search_files = knowledge_files

        results = []
        query_lower = query.lower()

        for filename, file_path in search_files.items():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find sections containing the query
                sections = _extract_matching_sections(content, query_lower)

                if sections:
                    results.append({"file": filename, "sections": sections})

            except Exception as e:
                continue  # Skip files that can't be read

        return {"status": "success", "query": query, "results": results, "files_searched": list(search_files.keys())}

    except Exception as e:
        return {"status": "error", "error_message": f"Failed to search knowledge: {str(e)}"}


def _extract_matching_sections(content: str, query: str) -> List[Dict[str, str]]:
    """Extract sections from markdown content that match the query.

    Args:
        content: Markdown content to search
        query: Search query (lowercase)

    Returns:
        List of matching sections with headers and content
    """
    sections = []
    lines = content.split("\n")
    current_section = None
    current_content = []

    for line in lines:
        # Check if this is a header line
        if line.startswith("#"):
            # Save previous section if it matched
            if current_section and current_content:
                section_text = "\n".join(current_content).lower()
                if query in section_text or query in current_section.lower():
                    sections.append({"header": current_section, "content": "\n".join(current_content).strip()})

            # Start new section
            current_section = line
            current_content = []
        else:
            current_content.append(line)

    # Check final section
    if current_section and current_content:
        section_text = "\n".join(current_content).lower()
        if query in section_text or query in current_section.lower():
            sections.append({"header": current_section, "content": "\n".join(current_content).strip()})

    return sections


def get_class_information(class_name: str) -> Dict[str, Any]:
    """Get detailed information about a D&D class.

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


def get_available_knowledge() -> Dict[str, Any]:
    """List all available knowledge files and their descriptions.

    Returns:
        Dictionary with available knowledge files
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


def get_session_management_guidance(topic: Optional[str] = None) -> Dict[str, Any]:
    """Get session management guidance from knowledge base.

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
