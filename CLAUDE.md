# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

D&D DM Agent - An AI Dungeon Master assistant built with Claude Agent SDK. Single-agent architecture with 2 core custom tools for dice rolling and campaign management. Character management, D&D knowledge, and DM guidance accessed via skills system.

## Package Management

**This project uses `uv` for Python package management.**

- All Python commands MUST be run with `uv run` prefix
- Examples: `uv run pytest`, `uv run python -m module`, `uv run ruff`
- Dependencies are managed in `pyproject.toml`

## Commands

```bash
# Run the agent (interactive mode)
uv run python -m dnd_dm_agent.claude_agent "your prompt here"

# Run tests
uv run pytest tests/

# Run a single test file
uv run pytest tests/test_utility_tools.py

# Run a specific test
uv run pytest tests/test_utility_tools.py::test_roll_dice_basic

# Run integration tests (requires ANTHROPIC_API_KEY)
uv run pytest tests/integration/

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Architecture

### Core Structure
- **`dnd_dm_agent/claude_agent.py`** - Main agent using Claude Agent SDK with 2 custom tools
- **`dnd_dm_agent/tools/`** - Custom tool implementations:
  - `utility_tools.py` - Dice rolls (`roll_dice`)
  - `campaign_instance_tools.py` - Campaign instance creation (`create_campaign_instance`)
- **`.claude/skills/`** - Skills system for D&D content:
  - `character-management/` - Character CRUD via markdown files (uses built-in Write/Read/Edit tools)
  - `dnd-knowledge-store/` - D&D 5e reference library (classes, spells, monsters, DM guidance)
  - `campaign-guide/` - Campaign loading and story tracking
  - `dnd-dm/` - DM techniques and session guidance
- **`campaigns/`** - Campaign skeletons (Acts → Beats structure) and active instances




## Code Style

- Python 3.13
- Line length: 120 characters
- Ruff for linting/formatting (E, F, W, I rules)
- Double quotes, space indent
