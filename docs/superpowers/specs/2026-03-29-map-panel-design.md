# Map Panel Design

## Goal
Replace `MapPlaceholder` with a live map panel that shows a location graph during exploration and a tactical grid during combat. The DM agent narrates naturally; bookkeeping writes map state; the frontend polls and renders.

## Architecture
- **DM agent** narrates spatial changes explicitly (guided by map skill) — does not write files
- **Bookkeeping** owns `map_state.json` — writes after each turn, same pattern as character files
- **Server** merges static terrain (campaign template) with dynamic tokens (instance) at the API layer
- **Frontend** polls one endpoint, renders exploration graph or combat grid based on `mode`

## Tech Stack
- Python / FastAPI (existing server)
- React + TypeScript (existing frontend)
- SVG for both map modes (no new libraries)

---

## 1. Room IDs in `locations.md`

`locations.md` currently has prose descriptions with no structured identifiers. Bookkeeping needs stable snake_case ids to write the `room` field in `map_state.json`, and the server uses that field to look up static map files.

Add a `**Room ID:**` field to each location section in `locations.md`:

```markdown
## Wizard's Tower Brewing Co.

**Room ID:** `wizards_tower_brewing`

**Description**: Successful craft brewery...
```

The room id must be:
- snake_case, no spaces
- Stable across the campaign (never rename once play starts)
- Matching the filename stem of its static map file (if one exists)

Update `available_campaigns/a_most_potent_brew/locations.md` with room ids for all locations. The campaign template `locations.md` is the canonical id reference — bookkeeping reads it to know valid ids.

---

## 2. Static Map Files (Campaign Template)

Static room layout lives at:
```
available_campaigns/{campaign}/maps/{room_id}.json
```

Schema:
```json
{
  "room": "brewery_cellars",
  "label": "The Brewery Cellars",
  "grid": {"width": 15, "height": 10},
  "terrain": [
    {"type": "wall", "x1": 6, "y1": 0, "x2": 6, "y2": 5},
    {"type": "obstacle", "label": "barrel", "x": 3, "y": 4},
    {"type": "obstacle", "label": "hole in wall", "x": 12, "y": 2}
  ]
}
```

Terrain types:
- `wall` — impassable barrier, defined by `x1,y1` to `x2,y2`
- `obstacle` — single-cell object, defined by `x,y`, has a `label`
- `difficult_terrain` — slows movement, defined by `x1,y1` to `x2,y2`

Not every room needs a map file. Rooms without one render tokens on a plain grid (combat mode) or as graph nodes (exploration mode).

Create `maps/brewery_cellars.json` for `a_most_potent_brew` as the reference example. Other rooms can be added incrementally.

---

## 3. Map Skill

New skill at `.claude/skills/map/SKILL.md`. Single file, no sub-files.

```yaml
---
name: map
description: Guides when and how to narrate spatial context. Use when the party moves to a new location or when combat involves positioning. Does not write files — bookkeeping handles map_state.json updates based on the DM's narrative.
allowed-tools: []
---
```

Content sections:

**When spatial context matters:**
- Party enters a new room or area → name it explicitly, mention visible connections to other areas
- Combat with 3+ combatants or meaningful terrain → describe starting positions and terrain features
- Token moves → state direction and relative position ("Thork moves north, now beside the barrel" not "Thork moves closer")
- Skip map narration for trivial skirmishes (1-2 enemies, open space, over in 1-2 turns) — log entry is enough

**Narration patterns for bookkeeping to extract:**
- Location: "The party enters the brewery cellars" → bookkeeping sets `room: "brewery_cellars"`
- Movement: "Thork charges north, ending up adjacent to rat_1" → bookkeeping infers position
- Combat start: "Initiative order: Thork (18), rat_1 (12), rat_2 (9)" → bookkeeping sets initiative
- HP change: already handled by character-management skill
- Combat end: "The last rat falls" → bookkeeping switches mode to exploration

**What the DM does not do:**
- Does not write `map_state.json`
- Does not state grid coordinates ("moves to 3,7") — relative narrative only
- Does not reference this skill mid-combat for every action — narrate naturally, bookkeeping extracts

---

## 4. Bookkeeping Checklist Extension

Add Step 4 to `campaign_tracking.md` post-turn checklist:

```markdown
**Step 4 — Update map state if location or combat state changed**:
- Find map state: `campaigns/{instance}/map_state.json`
- Read `locations.md` to confirm valid room ids before writing

**Exploration (party moved to new area):**
- Write `mode: "exploration"`, `room: "{room_id}"` (use id from locations.md)
- Update `graph.party_location` to the new room id
- Mark node `visited: true` if first visit
- Build graph nodes/edges from locations.md if not yet initialised

**Combat start:**
- Write `mode: "combat"`, `room: "{current_room_id}"`
- Initialise tokens: party HP from character files, enemy HP from encounters.md stat blocks
- Token type: `"party"` or `"enemy"`
- Infer starting positions from DM's narrative (relative placement, not coordinates)
- Set `initiative` order and `current_turn` from DM's narration
- Set `round: 1`

**Mid-combat (after each significant action):**
- Update token HP and conditions from DM's narrative
- Update token position if DM described movement
- Advance `current_turn` and `round` as turns pass
- Mark dead tokens with `conditions: ["dead"]` — do not remove from file

**Combat end:**
- Write `mode: "exploration"`, preserve `room` and `graph`
- Drop `tokens`, `initiative`, `current_turn`, `round` fields

**When to skip:**
- Purely conversational exchange with no movement, combat, or scene change
```

---

## 5. API Endpoint

### `GET /api/map/{instance}`

**Server logic:**
1. Read `campaigns/{instance}/map_state.json` — return 404 with `{"mode": null}` if absent
2. Extract `room` field
3. Read `campaign_progress.md` to get campaign template name (existing `_parse_instance_meta` pattern)
4. If room is set: attempt to read `available_campaigns/{campaign}/maps/{room}.json`
5. Merge: static fields (`grid`, `terrain`) + dynamic fields (everything from map_state.json)
6. Return merged object

**If no static map file:** return dynamic layer only (no `grid`, no `terrain`).

**Response shape** matches the merged schema from ADR-014/016.

**Error cases:**
- `map_state.json` absent → `{"mode": null}` (frontend shows placeholder)
- `maps/{room}.json` absent → return dynamic only, no error

### Frontend polling

Frontend polls `GET /api/map/{instance}` every 3 seconds while a session is active. On `mode: null` response, renders placeholder. Mode switches trigger a re-render.

---

## 6. Frontend MapPanel Component

Replace `MapPlaceholder` with `MapPanel` in `frontend/src/components/map/`.

### Component structure

```
frontend/src/components/map/
  MapPanel.tsx          — top-level, fetches data, switches between modes
  ExplorationMap.tsx    — renders location graph (SVG)
  CombatMap.tsx         — renders tactical grid (SVG)
  MapPanel.css
```

### `MapPanel.tsx`

- Polls `GET /api/map/{instance}` every 3 seconds
- `mode === null` or no data → renders placeholder text ("Map loading...")
- `mode === "exploration"` → renders `<ExplorationMap>`
- `mode === "combat"` → renders `<CombatMap>`
- Passes full merged map object as props

Receives `instance` prop from `App.tsx` (already available in session state).

### `ExplorationMap.tsx`

SVG-based location graph:
- Each node: rounded rect with room label, filled differently for visited vs unvisited
- Current party location: highlighted node (distinct colour)
- Edges: lines between connected nodes
- Layout: simple force-directed or manual positioning based on node count

Props: `{ graph: { nodes, edges, party_location } }`

### `CombatMap.tsx`

SVG-based tactical grid:
- Grid lines at cell boundaries (cell size: 40px)
- Terrain: walls as thick lines, obstacles as labelled shapes
- Tokens: coloured circles — blue for party, red for enemies, grey for dead
- Token label: name + current HP (e.g. "Thork 7/12")
- Current turn: token has a highlight ring
- Hover: show full token details (conditions, max HP)

Props: `{ grid, terrain, tokens, current_turn }`

If `grid` is absent (no static map file), render tokens on an implicit grid sized to fit all token positions.

### `MapPanel.css`

Extends existing panel styling. Map fills the top panel area. SVG scales to fill available space.

---

## ADR Compliance Notes

- **ADR-002 (JSON exception):** `map_state.json` and `maps/{room_id}.json` use JSON, not markdown. ADR-002 has been updated to permit this for coordinate-based spatial data that cannot be expressed cleanly in markdown.
- **ADR-010 (eval gate):** Adding Step 4 to `campaign_tracking.md` modifies `.claude/skills/campaign-guide/`. Before merging that change, run the bookkeeping eval suite and confirm all 4 scenarios pass:
  ```bash
  uv run pytest tests/integration/test_bookkeeping_evals.py -v
  ```

---

## Out of Scope

- Option B (structured DM output block for precise coordinates) — documented in ADR-015, implement only if grid precision becomes a concrete complaint
- Drag-and-drop token repositioning by the player
- Fog of war
- Map file authoring UI — campaign authors write JSON directly
- Maps for campaigns other than `a_most_potent_brew` (can be added incrementally)
