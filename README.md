# D&D DM Agent

An AI Dungeon Master for D&D 5e, built on the Claude Agent SDK. Features a web-based VTT-style interface with chat narration, character tracking, and dice rolling.

## Prerequisites

- Python 3.13+ with [uv](https://docs.astral.sh/uv/)
- Node.js 18+
- `ANTHROPIC_API_KEY` set in `.env`

## Running the App

The app requires two services running simultaneously — open two terminals.

**Terminal 1 — Backend API (port 8000):**
```bash
uv run uvicorn dnd_dm_agent.server:app --reload --port 8000
```

**Terminal 2 — Frontend (port 5173):**
```bash
cd frontend && npm run dev
```

Then open **http://localhost:5173** in your browser.

## CLI / REPL (no frontend)

```bash
# Single prompt
uv run python -m dnd_dm_agent.claude_agent "your prompt here"

# Interactive session
uv run python -m dnd_dm_agent.interactive
# or
dnd-repl
```

## Development

```bash
# Install dependencies
uv sync
cd frontend && npm install

# Run tests
uv run pytest tests/

# Lint / format
uv run ruff check .
uv run ruff format .

# Debug logging
DND_LOG_LEVEL=DEBUG uv run uvicorn dnd_dm_agent.server:app --reload --port 8000
```

## Project Structure

```
dnd_dm_agent/
  claude_agent.py        # Core agent (Claude Agent SDK)
  server.py              # FastAPI WebSocket server
  interactive.py         # CLI REPL
  tools/
    utility_tools.py     # roll_dice tool
    campaign_instance_tools.py  # create_campaign_instance tool
frontend/
  src/
    App.tsx              # Main app state (useReducer)
    components/          # Layout, sidebar, chat, input, map
    hooks/               # useWebSocket
    services/            # characterParser
    types/               # WebSocket message types
campaigns/               # Active campaign instances
.claude/skills/          # D&D knowledge skills (character-management, dnd-knowledge-store, etc.)
docs/
  FRONTEND_PLAN.md       # Frontend architecture reference
```

## Architecture

```
Browser (React/TS @ :5173)
    │  WebSocket  ws://localhost:8000/ws/{session_id}
FastAPI Server  (:8000)
    │  ClaudeSDKClient (one per session)
Claude Agent SDK → Anthropic API
```
