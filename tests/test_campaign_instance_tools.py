"""Tests for campaign instance tools."""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch

from dnd_dm_agent.tools.campaign_instance_tools import create_campaign_instance, PROJECT_ROOT


@pytest.fixture
def temp_campaigns_dir():
    """Create a temporary directory for campaign instances."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    if temp_path.exists():
        shutil.rmtree(temp_path)


def test_create_campaign_instance_from_real_template(temp_campaigns_dir):
    """Test creating instance from actual a_most_potent_brew campaign."""
    with patch("dnd_dm_agent.tools.campaign_instance_tools.CAMPAIGNS_DIR", temp_campaigns_dir):
        result = create_campaign_instance("a_most_potent_brew", "test_party")

        # Check success
        assert result["status"] == "success"
        assert "a_most_potent_brew_test_party" in result["message"]

        # Check files copied from template
        instance_path = temp_campaigns_dir / "a_most_potent_brew_test_party"
        assert (instance_path / "campaign_guide.md").exists()
        assert (instance_path / "npcs.md").exists()
        assert (instance_path / "locations.md").exists()
        assert (instance_path / "encounters.md").exists()

        # Check campaign-specific files created
        assert (instance_path / "campaign_progress.md").exists()
        assert (instance_path / "campaign_log.md").exists()
        assert (instance_path / "characters").is_dir()

        # Verify content structure
        progress = (instance_path / "campaign_progress.md").read_text()
        assert "test_party" in progress
        assert "a_most_potent_brew" in progress
        assert "## Current Progress" in progress
        assert "## Party" in progress


def test_create_campaign_instance_already_exists(temp_campaigns_dir):
    """Test error when instance already exists."""
    with patch("dnd_dm_agent.tools.campaign_instance_tools.CAMPAIGNS_DIR", temp_campaigns_dir):
        result1 = create_campaign_instance("a_most_potent_brew", "test_party")
        assert result1["status"] == "success"

        result2 = create_campaign_instance("a_most_potent_brew", "test_party")
        assert result2["status"] == "error"
        assert "already exists" in result2["error_message"]
