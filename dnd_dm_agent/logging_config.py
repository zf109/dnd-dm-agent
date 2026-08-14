"""Logging configuration for DnD DM Agent."""

import logging
import os
import sys
from pathlib import Path

# Log directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure logging for the DnD DM Agent.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO
               Can be overridden by DND_LOG_LEVEL environment variable.

    Returns:
        Configured root logger instance
    """
    # Allow env var to override default
    level = os.environ.get("DND_LOG_LEVEL", level)

    root = logging.getLogger("dnd_dm_agent")
    root.setLevel(getattr(logging, level.upper()))

    # Avoid duplicate handlers
    if root.handlers:
        return root

    # %(name)s will show dnd_dm_agent / dnd_dm_agent.dm / dnd_dm_agent.bookkeeping etc.
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # File handler (DEBUG and above)
    file_handler = logging.FileHandler(LOG_DIR / "agent.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    return root


# All loggers inherit handlers and level from the parent "dnd_dm_agent" logger.
# The %(name)s in the format string automatically distinguishes them in output:
#   dnd_dm_agent             — server / general
#   dnd_dm_agent.dm          — DM agent turns
#   dnd_dm_agent.bookkeeping — bookkeeping subagent
setup_logging()
logger = logging.getLogger("dnd_dm_agent")
dm_logger = logging.getLogger("dnd_dm_agent.dm")
bookkeeping_logger = logging.getLogger("dnd_dm_agent.bookkeeping")
