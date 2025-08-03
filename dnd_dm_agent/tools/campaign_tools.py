"""Campaign management tools for the DnD DM Agent."""

from pathlib import Path
from typing import Dict, Any

# Base directory for campaigns
CAMPAIGNS_DIR = Path(__file__).parent.parent.parent / "campaigns"


def list_campaigns() -> Dict[str, Any]:
    """List all available campaigns.
    
    Returns:
        Dictionary with campaign information
    """
    try:
        if not CAMPAIGNS_DIR.exists():
            return {
                "status": "success",
                "campaigns": [],
                "message": "No campaigns found. Create campaigns using campaign creation tools."
            }
        
        campaigns = []
        for campaign_path in CAMPAIGNS_DIR.iterdir():
            if campaign_path.is_dir() and (campaign_path / "campaign_skeleton.md").exists():
                campaigns.append(campaign_path.name)
        
        return {
            "status": "success",
            "campaigns": campaigns,
            "total_campaigns": len(campaigns)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to list campaigns: {str(e)}"
        }


def load_campaign(campaign_name: str) -> Dict[str, Any]:
    """Load a campaign skeleton for reference during gameplay.
    
    Args:
        campaign_name: Name of the campaign to load
        
    Returns:
        Dictionary with campaign skeleton content
    """
    try:
        campaign_path = CAMPAIGNS_DIR / campaign_name
        skeleton_path = campaign_path / "campaign_skeleton.md"
        
        if not skeleton_path.exists():
            available = list_campaigns()
            return {
                "status": "error",
                "error_message": f"Campaign '{campaign_name}' not found. Available campaigns: {available.get('campaigns', [])}"
            }
        
        with open(skeleton_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "status": "success",
            "campaign_name": campaign_name,
            "content": content
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to load campaign: {str(e)}"
        }