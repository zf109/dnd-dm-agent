# ADR-016: Map API and Room Resolution

## Status
Accepted

## Context
ADR-014 establishes two layers of map data:
- **Static** — room layout, grid, terrain/furniture — in `available_campaigns/{campaign}/maps/{room_id}.json`
- **Dynamic** — tokens, HP, initiative, mode — in `campaigns/{instance}/map_state.json`

The frontend needs a single, renderable map object. It should not be responsible for resolving which campaign template an instance belongs to, nor for merging two files.

In a real tabletop session the DM physically selects and places the map. In this system, bookkeeping sets `room` in `map_state.json` when the party moves — that field is the bridge between the two layers.

## Decision

**The server merges static and dynamic map data and exposes a single endpoint.**

### Endpoint

```
GET /api/map/{instance}
```

Returns a single merged map object. The frontend calls this endpoint and renders what it receives — it has no knowledge of two source files.

### Server merge logic

1. Read `campaigns/{instance}/map_state.json` (dynamic layer)
2. Extract `room` field (e.g. `"brewery_cellar"`)
3. Resolve the campaign template from the instance (see below)
4. Read `available_campaigns/{campaign}/maps/{room}.json` if it exists (static layer)
5. Merge: static fields (`grid`, `terrain`) + dynamic fields (`mode`, `tokens`, `initiative`, etc.)
6. Return merged object

If no static map file exists for the room, return the dynamic layer only — frontend renders tokens without a background layout.

Example merged response:
```json
{
  "mode": "combat",
  "room": "brewery_cellar",
  "grid": {"width": 15, "height": 10},
  "terrain": [
    {"type": "wall", "x1": 6, "y1": 0, "x2": 6, "y2": 5},
    {"type": "obstacle", "label": "barrel", "x": 3, "y": 4}
  ],
  "tokens": {
    "thork": {"x": 3, "y": 2, "hp": 7, "max_hp": 12, "conditions": [], "type": "party"},
    "rat_1": {"x": 8, "y": 5, "hp": 4, "max_hp": 7, "conditions": [], "type": "enemy"}
  },
  "initiative": ["thork", "rat_1"],
  "current_turn": "rat_1",
  "round": 2
}
```

### Template resolution

The server resolves the campaign template from `campaign_progress.md` in the instance directory. This is more reliable than parsing the instance directory name, which would break if template names contain underscores.

`campaign_progress.md` already stores `Campaign:` — the server reads this field. No new state required.

### Room naming contract

The `room` value written by bookkeeping must match the filename stem in `maps/`. For example:
- `"room": "brewery_cellar"` → looks up `maps/brewery_cellar.json`
- `"room": "tavern_main_hall"` → looks up `maps/tavern_main_hall.json`

Room ids come from `locations.md` in the campaign template — each location has an `id` field. Bookkeeping uses these ids, not freeform descriptions. The map skill and bookkeeping instructions must make this explicit.

Campaign authors must name map files to match location ids in `locations.md`.

## Consequences
- **Frontend is simple.** One endpoint, one object, no file resolution logic on the client.
- **Server owns the merge.** Static and dynamic layers are an implementation detail hidden behind the API.
- **Room id is a contract.** Bookkeeping and campaign authors must use consistent ids. A mismatch means no static map loads — tokens render without background, which degrades gracefully.
- **Constraint:** Do not expose separate static/dynamic endpoints to the frontend. The merge belongs on the server.
- **Constraint:** Room ids must be stable identifiers (snake_case, no spaces), not display names. Display names live in `locations.md` as `label` fields.
