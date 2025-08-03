"""Tests for session tools."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

from dnd_dm_agent.tools.session_tools import get_session_log


# Mock content for testing
MOCK_SESSION_LOG_CONTENT = """# Test Session - Session Log

**DM:** Test DM
**Created:** 2025-01-27 15:30

## Session History

### Session 1
*2025-01-27*

- Game session created
- Character 'Thorin' joined the session
- [16:30] The party enters the tavern
- [17:00] Met the mysterious hooded figure
"""


def test_get_session_log_success():
    """Test getting session log successfully."""
    mock_sessions_dir = MagicMock()
    mock_session_path = MagicMock()
    mock_log_path = MagicMock()
    
    mock_sessions_dir.__truediv__.return_value = mock_session_path
    mock_session_path.exists.return_value = True
    mock_session_path.__truediv__.return_value = mock_log_path
    mock_log_path.exists.return_value = True
    
    with patch("dnd_dm_agent.tools.session_tools.SESSIONS_DIR", mock_sessions_dir):
        with patch("builtins.open", mock_open(read_data=MOCK_SESSION_LOG_CONTENT)):
            result = get_session_log("test_session")
            
            assert result["status"] == "success"
            assert result["session_name"] == "test_session"
            assert "Session History" in result["content"]