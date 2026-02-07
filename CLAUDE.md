# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

D&D DM Agent - An AI Dungeon Master assistant built with Claude Agent SDK. Single-agent architecture with 5 core custom tools for character management, dice rolling, and session tracking. D&D knowledge accessed via skills system.

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
uv run pytest tests/test_knowledge_tools.py

# Run a specific test
uv run pytest tests/test_knowledge_tools.py::test_lookup_knowledge_finds_content

# Run integration tests (requires ANTHROPIC_API_KEY)
uv run pytest tests/integration/

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Architecture

### Core Structure
- **`dnd_dm_agent/claude_agent.py`** - Main agent using Claude Agent SDK with 5 custom tools
- **`dnd_dm_agent/tools/`** - Tool implementations (used by claude_agent.py):
  - `character_tools/` - Character CRUD, validation, schema (D&D 5e character structure)
  - `utility_tools.py` - Dice rolls, game state tracking
- **`.claude/skills/dnd-knowledge-store/`** - D&D 5e knowledge skill with markdown references
  - `knowledge/` - Classes, spells, monsters, DM guidance (moved from dnd_dm_agent/)
- **`campaigns/`** - Campaign skeletons (Acts → Beats structure)




## Code Style

- Python 3.13
- Line length: 120 characters
- Ruff for linting/formatting (E, F, W, I rules)
- Double quotes, space indent
