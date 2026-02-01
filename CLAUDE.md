# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

D&D DM Agent - An AI Dungeon Master assistant built with Google ADK (Agent Development Kit). Single-agent architecture with 17 specialized tools for character management, D&D knowledge lookup, session tracking, and campaign management.

## Commands

```bash
# Run the agent (interactive mode)
adk run dnd_dm_agent

# Run tests
pytest tests/

# Run a single test file
pytest tests/test_knowledge_tools.py

# Run a specific test
pytest tests/test_knowledge_tools.py::test_lookup_knowledge_finds_content

# Lint and format
ruff check .
ruff format .
```

## Architecture

### Core Structure
- **`dnd_dm_agent/agent.py`** - Main agent definition (dungeon_master agent with Claude 3.5 Sonnet via LiteLLM)
- **`dnd_dm_agent/tools/`** - All tool implementations:
  - `character_tools/` - Character CRUD, validation, schema (D&D 5e character structure)
  - `knowledge_tools.py` - D&D knowledge base search (classes, spells, monsters)
  - `session_tools.py` - Game session management and logging
  - `campaign_tools.py` - Campaign skeleton loading
  - `utility_tools.py` - Dice rolls, game state tracking
- **`dnd_dm_agent/knowledge/`** - Markdown-based D&D 5e knowledge base
- **`campaigns/`** - Campaign skeletons (Acts → Beats structure)
- **`config/llm_engine.py`** - Multi-provider LLM configuration (Anthropic, OpenAI, Google, etc.)

### Data Flow
1. Sessions created in `dnd_dm_agent/game_sessions/[session_name]/`
2. Characters stored as JSON in session's `characters/` subdirectory
3. Session logs tracked in `session_log.md` with timestamps
4. Knowledge searched via recursive glob + regex pattern matching

### Campaign Structure
Campaigns use a two-level nesting: Acts (major story phases) → Beats (individual accomplishments). Stored in `campaigns/[name]/campaign_skeleton.md`.

## Testing Patterns

- Test files mirror tool modules: `test_knowledge_tools.py`, `test_character_tools.py`, etc.
- Mock data uses `MOCK_*_CONTENT` constants
- Knowledge tools tested with mock markdown content injected via monkeypatching

## Code Style

- Python 3.13
- Line length: 120 characters
- Ruff for linting/formatting (E, F, W, I rules)
- Double quotes, space indent

## Key Behaviors

- Always create a game session BEFORE character creation
- Use `tool_validate_character_readiness` before starting adventures
- Call `update_session_log` immediately after `manage_game_state` changes
- Knowledge search uses case-insensitive regex across all markdown files in knowledge/
