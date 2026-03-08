# Frontend Plan: React + TypeScript for D&D DM Agent

## Context

The project is a conversational AI Dungeon Master built on Claude Agent SDK. It currently has only a CLI/REPL interface. We're adding a web frontend to make it a proper VTT-style app: chat panel, character sidebar, and a reserved map panel area (map functionality TBD, placeholder for now). Tech stack: React + TypeScript (Vite) for frontend, FastAPI + WebSockets for the backend API layer.

---

## Architecture

```
Browser (React/TS/Vite @ :5173)
    |  WebSocket  ws://localhost:8000/ws/{session_id}
FastAPI Server  (dnd_dm_agent/server.py @ :8000)
    |  ClaudeSDKClient (one per WS connection, tied to connection lifetime)
Claude Agent SDK → Anthropic API
```

**Session lifetime = WebSocket connection lifetime.** When the browser disconnects, the `ClaudeSDKClient` tears down. Conversation history resets on browser refresh (acceptable for now; can be extended with persistence later).

---

## UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  DnD DM Agent              [Campaign: xxx]    [● Connected]     │  ← AppHeader
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│  CHARACTER   │   MAP PANEL  (placeholder "Coming Soon")         │  ← ~60vh
│  SIDEBAR     │                                                  │
│  Name, HP    ├──────────────────────────────────────────────────┤
│  AC, Speed   │   CHAT / NARRATION LOG                          │  ← flex 1
│  Conditions  │   DM text (serif, gold left border)             │
│  Spell slots │   Dice results (parchment highlight box)        │
│              │   Player messages (right-aligned)               │
├──────────────┴──────────────────────────────────────────────────┤
│  [d4][d6][d8][d10][d12][d20]    [Type your action...]  [Send]  │  ← InputBar
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Backend — `dnd_dm_agent/server.py`

### 1a. Add dependencies to `pyproject.toml`
```toml
"fastapi>=0.115.0",
"uvicorn[standard]>=0.30.0",
```

### 1b. WebSocket Endpoint

Mirror the `interactive.py` pattern exactly — `ClaudeSDKClient` as an `async with` context manager:

```python
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    async with ClaudeSDKClient(options=get_options()) as client:
        async for raw in websocket.iter_text():
            msg = json.loads(raw)
            if msg["type"] == "user_input":
                await client.query(msg["content"])
                async for message in client.receive_response():
                    # stream text_chunk / tool_use / dice_roll / tool_result events
                    await websocket.send_json(...)
                await websocket.send_json({"type": "turn_complete"})
```

Key files to reference:
- `dnd_dm_agent/interactive.py` — exact `ClaudeSDKClient` pattern to mirror
- `dnd_dm_agent/claude_agent.py` — import `get_options()`, `process_message()`

### 1c. REST Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/health` | Health check |
| `GET /api/campaigns` | List active campaign instances from `campaigns/` dir |
| `GET /api/character/{campaign_instance}/{character_name}` | Read character markdown file |

### 1d. CORS
Allow `http://localhost:5173` (Vite dev server default port).

### 1e. WebSocket Message Protocol

**Client → Server:**
```json
{ "type": "user_input", "content": "I cast Sleep on the goblins!" }
```

**Server → Client (streaming):**
```jsonc
// DM narration text chunk
{ "type": "text_chunk", "content": "The goblins' eyes glaze over..." }

// Agent used a tool
{ "type": "tool_use", "tool_name": "mcp__dnd__roll_dice", "tool_input": {"notation": "5d8"} }

// Tool result (after agent gets response back)
{ "type": "tool_result", "tool_name": "mcp__dnd__roll_dice",
  "result": {"notation": "5d8", "individual_rolls": [3,7,2,5,8], "total": 25} }

// Turn finished — frontend should refresh character sidebar
{ "type": "turn_complete" }

// Error
{ "type": "error", "error": "rate_limit_exceeded" }
```

---

## Step 2: Frontend — `frontend/` directory

### 2a. Scaffold
```bash
npm create vite@latest frontend -- --template react-ts
```
**No Tailwind** — use CSS variables in `App.css` for the dark fantasy theme.

**Additional dependency:** `react-markdown` — renders DM narration markdown formatting.

### 2b. CSS Variables (dark fantasy theme)

```css
:root {
  --bg-primary:    #1a1a1a;
  --bg-secondary:  #2d2d2d;
  --bg-panel:      #252525;
  --accent-gold:   #c9a84c;
  --text-primary:  #e8e0d0;
  --text-muted:    #8a8070;
  --hp-red:        #8b2020;
  --border-color:  #3d3d3d;
  --font-serif:    'Cinzel', 'Palatino Linotype', serif;
  --font-sans:     'Segoe UI', system-ui, sans-serif;
  --sidebar-width: 260px;
}
```

Load Cinzel from Google Fonts in `index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap" rel="stylesheet">
```

### 2c. File Structure

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── main.tsx
    ├── App.tsx                   # useReducer state, WS message handler, layout root
    ├── App.css                   # CSS variables + global styles
    ├── types/
    │   └── messages.ts           # All WS message types + ChatEntry + CharacterData
    ├── hooks/
    │   ├── useWebSocket.ts       # WS connect + auto-reconnect, sendMessage
    │   └── useCharacter.ts       # HTTP GET /api/character + refresh on turn_complete
    ├── services/
    │   └── characterParser.ts    # Parse markdown character sheet → CharacterData
    └── components/
        ├── layout/
        │   ├── AppHeader.tsx         # Title bar, campaign name, WS status dot
        │   └── AppLayout.tsx         # CSS grid: sidebar | (map top / chat bottom)
        ├── sidebar/
        │   ├── CharacterSidebar.tsx  # Container
        │   ├── CharacterStats.tsx    # HP bar, AC, speed, spell slots
        │   └── ConditionBadge.tsx    # Status condition pill
        ├── map/
        │   └── MapPlaceholder.tsx    # "Map — Coming Soon" panel
        ├── chat/
        │   ├── ChatLog.tsx           # Auto-scrolling list of ChatEntry
        │   ├── DMMessage.tsx         # Serif, gold left border, react-markdown
        │   ├── PlayerMessage.tsx     # Right-aligned, plain text
        │   ├── DiceRollEvent.tsx     # Individual rolls + total, parchment bg
        │   ├── ToolUseEvent.tsx      # "DM is checking lore..." indicator
        │   └── TypingIndicator.tsx   # Animated dots while agent is thinking
        └── input/
            ├── InputBar.tsx          # Container: dice buttons + text input
            ├── DiceButtons.tsx       # d4/d6/d8/d10/d12/d20 quick-roll buttons
            └── MessageInput.tsx      # Textarea + Send button
```

### 2d. State Management

`useReducer` in `App.tsx` — no external library needed.

```typescript
type ChatEntry =
  | { id: string; kind: 'player'; content: string }
  | { id: string; kind: 'dm'; content: string; isComplete: boolean }
  | { id: string; kind: 'dice'; notation: string; rolls: number[]; total: number }
  | { id: string; kind: 'tool_indicator'; tool_name: string };

type AppState = {
  chatEntries: ChatEntry[];
  isAgentTyping: boolean;
  currentDMEntryId: string | null;   // ID of in-progress DM message bubble
  character: CharacterData | null;
  campaignInstance: string;
  sessionId: string;                 // UUID from sessionStorage
};
```

Key reducer actions:
- `APPEND_TEXT_CHUNK` — appends content to current DM entry (or creates new one)
- `TURN_COMPLETE` — marks current DM entry `isComplete: true`, clears typing state
- `ADD_DICE_RESULT` — adds dice entry to chat log
- `SET_CHARACTER` — updates character sidebar data

### 2e. Character Parsing (`characterParser.ts`)

Regex patterns derived from `campaigns/.../characters/sapphire_star.md` format:

```typescript
const HP_REGEX    = /\*\*Hit Points\*\*\s*\|\s*(\d+)\s*\/\s*(\d+)/;
const AC_REGEX    = /\*\*Armor Class \(AC\)\*\*\s*\|\s*(\d+)/;
const SPEED_REGEX = /\*\*Speed\*\*\s*\|\s*(\d+)/;
const NAME_REGEX  = /^#\s+(.+?)\s+-\s+Level/m;
const SPELL_REGEX = /\*\*1st\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)/;  // total | used
```

Called after each `turn_complete` event: fetch `/api/character/{campaign}/{name}` → parse markdown → dispatch `SET_CHARACTER`.

### 2f. Dice Quick Buttons

Each button sends `{ "type": "user_input", "content": "Roll a d20" }` to the WebSocket. The DM agent handles this naturally by calling the `roll_dice` tool and narrating the result.

---

## Relevant Claude Skills to Install

Two official skills from [github.com/anthropics/skills](https://github.com/anthropics/skills):

### `frontend-design`
- **Purpose:** Guides bold, characterful UI design. Prevents generic "AI slop" aesthetics.
- **When to use:** Invoke before writing UI components for design guidance on typography (Cinzel), CSS variable palettes, motion, and spatial composition.

### `webapp-testing`
- **Purpose:** Browser-based frontend testing.
- **When to use:** After the chat panel and WebSocket are working, use to write tests.

**Install both:**
```bash
git clone https://github.com/anthropics/skills /tmp/anthropic-skills
cp -r /tmp/anthropic-skills/skills/frontend-design .claude/skills/
cp -r /tmp/anthropic-skills/skills/webapp-testing .claude/skills/
```

---

## Running Both Services

**Terminal 1 — Backend:**
```bash
uv run uvicorn dnd_dm_agent.server:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend && npm install && npm run dev
# Opens at http://localhost:5173
```

---

## Implementation Order

1. Add `fastapi`, `uvicorn[standard]` to `pyproject.toml`
2. Create `dnd_dm_agent/server.py` — health endpoint first, verify server starts
3. Add WebSocket endpoint, test with browser dev tools
4. Add character + campaigns REST endpoints
5. Scaffold `frontend/` with Vite
6. Set up CSS variables, `AppLayout.tsx` CSS grid
7. Implement `useWebSocket.ts` hook
8. Build `App.tsx` reducer + WS message handler
9. Build `ChatLog` + message components (`DMMessage`, `PlayerMessage`, `DiceRollEvent`)
10. Build `InputBar` + `DiceButtons` + `MessageInput`
11. Build `CharacterSidebar` + `characterParser.ts`
12. Add `MapPlaceholder`, `AppHeader` with campaign/status display, polish

---

## Verification Checklist

- [ ] `uv run uvicorn dnd_dm_agent.server:app --reload` starts without errors
- [ ] `GET http://localhost:8000/api/health` returns 200
- [ ] WebSocket connects from browser: no CORS errors in DevTools console
- [ ] Send `{"type":"user_input","content":"Hello, who are you?"}` → receive `text_chunk` stream + `turn_complete`
- [ ] Frontend renders DM narration in serif gold-bordered bubble
- [ ] Dice button click → DM rolls dice and narrates result in chat
- [ ] Character sidebar shows HP/AC/speed when a campaign with a character is active
