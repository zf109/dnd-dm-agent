"""Tests for campaign tools."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, mock_open, patch

from dnd_dm_agent.tools.campaign_tools import (
    list_campaigns,
    load_campaign,
)


# Mock content for testing
MOCK_CAMPAIGN_SKELETON_CONTENT = """# A Most Potent Brew - Campaign Skeleton

## Campaign Overview
- **Level Range**: 1-2 (starting at 1st, ending at 2nd level)
- **Duration**: Single session (2-4 hours)

## Act 1: The Brewery Investigation (Levels 1-2)
**Story Goal**: Solve the giant rat problem
"""


def test_list_campaigns_success():
    """Test listing campaigns successfully."""
    mock_campaigns_dir = MagicMock()
    mock_campaigns_dir.exists.return_value = True
    
    mock_campaign = MagicMock()
    mock_campaign.name = "a_most_potent_brew"
    mock_campaign.is_dir.return_value = True
    
    mock_skeleton = MagicMock()
    mock_skeleton.exists.return_value = True
    mock_campaign.__truediv__.return_value = mock_skeleton
    
    mock_campaigns_dir.iterdir.return_value = [mock_campaign]
    
    with patch("dnd_dm_agent.tools.campaign_tools.CAMPAIGNS_DIR", mock_campaigns_dir):
        result = list_campaigns()
        
        assert result["status"] == "success"
        assert "a_most_potent_brew" in result["campaigns"]


def test_load_campaign_success():
    """Test loading a campaign successfully."""
    mock_campaigns_dir = MagicMock()
    mock_campaign_path = MagicMock()
    mock_skeleton_path = MagicMock()
    
    mock_campaigns_dir.__truediv__.return_value = mock_campaign_path
    mock_campaign_path.__truediv__.return_value = mock_skeleton_path
    mock_skeleton_path.exists.return_value = True
    
    with patch("dnd_dm_agent.tools.campaign_tools.CAMPAIGNS_DIR", mock_campaigns_dir):
        with patch("builtins.open", mock_open(read_data=MOCK_CAMPAIGN_SKELETON_CONTENT)):
            result = load_campaign("a_most_potent_brew")
            
            assert result["status"] == "success"
            assert result["campaign_name"] == "a_most_potent_brew"
            assert "Campaign Overview" in result["content"]