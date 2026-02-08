"""Campaign instance management tools for DnD DM Agent."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Base directory for campaign instances (project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
CAMPAIGNS_DIR = PROJECT_ROOT / "campaigns"


def create_campaign_instance(
    campaign_template: str,
    instance_name: str,
) -> Dict[str, Any]:
    """Create a new campaign instance from a template.

    Args:
        campaign_template: Name of the campaign template (e.g., "a_most_potent_brew")
        instance_name: Unique name for this campaign instance (e.g., "party1", "weekenders")

    Returns:
        Dictionary with campaign creation status and details

    Example:
        create_campaign_instance("a_most_potent_brew", "party1")
        Creates: campaigns/a_most_potent_brew_party1/
    """
    try:
        # Create campaigns directory if it doesn't exist
        CAMPAIGNS_DIR.mkdir(exist_ok=True)

        # Create campaign instance folder
        campaign_instance_name = f"{campaign_template}_{instance_name}"
        instance_path = CAMPAIGNS_DIR / campaign_instance_name

        if instance_path.exists():
            return {
                "status": "error",
                "error_message": f"Campaign instance '{campaign_instance_name}' already exists"
            }

        instance_path.mkdir(exist_ok=True)

        # Create characters directory
        characters_path = instance_path / "characters"
        characters_path.mkdir(exist_ok=True)

        # Create campaign_progress.md
        progress_path = instance_path / "campaign_progress.md"
        with open(progress_path, "w") as f:
            f.write(f"# {campaign_template.replace('_', ' ').title()} - {instance_name}\n\n")
            f.write(f"**Instance:** {instance_name}\n")
            f.write(f"**Template:** {campaign_template}\n")
            f.write(f"**Created:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write("## Current Progress\n")
            f.write("- **Act:** Not started\n")
            f.write("- **Beat:** Not started\n\n")
            f.write("## Party\n\n")
            f.write("## Key Decisions\n\n")

        # Create campaign_log.md for event logging
        log_path = instance_path / "campaign_log.md"
        with open(log_path, "w") as f:
            f.write(f"# {campaign_template.replace('_', ' ').title()} - Event Log\n\n")
            f.write(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')}** - Campaign instance created\n\n")

        # Copy campaign files from template if they exist
        template_path = PROJECT_ROOT / "available_campaigns" / campaign_template
        if template_path.exists():
            files_to_copy = ["campaign_guide.md", "npcs.md", "locations.md", "encounters.md"]
            copied_files = []

            for filename in files_to_copy:
                src_file = template_path / filename
                if src_file.exists():
                    dst_file = instance_path / filename
                    dst_file.write_text(src_file.read_text())
                    copied_files.append(filename)

            copy_message = f"Copied: {', '.join(copied_files)}" if copied_files else "No files copied"
        else:
            copy_message = f"Template '{campaign_template}' not found"

        return {
            "status": "success",
            "message": f"Campaign instance '{campaign_instance_name}' created!",
            "instance_path": str(instance_path),
            "files_copied": copy_message,
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to create campaign instance: {str(e)}"
        }
