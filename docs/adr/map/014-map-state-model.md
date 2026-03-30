# ADR-014: Map State Model

## Status
Accepted

## Context
ADR-013 defines two map modes. This ADR defines what `map_state.json` contains and where each piece of game information lives.

Three models were considered:

**A — Thin map (positions only):** `map_state.json` stores spatial data only; HP and stats stay in existing character and encounter files. Simple, no duplication — but enemy HP has no natural home (encounters.md is static reference data, not mutable combat state), and the DM agent must cross-reference multiple files per turn.

**B — Combat notepad:** `map_state.json` is the DM's single combat reference: positions + current HP snapshot + initiative + conditions. Enemy HP lives here because it is ephemeral (rats die, encounter is over). Party HP is a snapshot from character files for convenience.

**C — Split map + combat tracker:** Two files with clear roles: `map_state.json` for spatial, `combat_state.json` for initiative/HP/conditions. Clean separation — but two files to update per action, and more complex skill instructions.

Model B was chosen. During design, an additional distinction emerged between **static** and **dynamic** map data:

- **Static data** — room layout, walls, doors, furniture, fixed obstacles. These are defined by the campaign and are the same for every instance. Barrels and holes in the wall don't move between playthroughs. This data belongs in the campaign template.
- **Dynamic data** — token positions, HP, initiative, current turn, conditions. These change per session and per combat. This data belongs in the instance's `map_state.json`.

`map_state.json` holds only dynamic state. The frontend merges static terrain from the campaign template with dynamic tokens from `map_state.json` when rendering a room.

## Decision

Use **Model B — the combat notepad**, with static/dynamic separation. `map_state.json` is the DM's single dynamic combat reference. Static room layout lives in the campaign template.

### Campaign template: static room maps

Each room with meaningful layout has a file at:
```
available_campaigns/{campaign}/maps/{room_id}.json
```

Example `maps/brewery_cellar.json`:
```json
{
  "room": "brewery_cellar",
  "label": "The Brewery Cellars",
  "grid": {"width": 15, "height": 10},
  "terrain": [
    {"type": "wall", "x1": 6, "y1": 0, "x2": 6, "y2": 5},
    {"type": "obstacle", "label": "barrel", "x": 3, "y": 4},
    {"type": "obstacle", "label": "hole in wall", "x": 12, "y": 2}
  ]
}
```

Not every room needs a map file. Simple rooms with no meaningful terrain can be omitted — the frontend renders tokens without a background layout.

### Instance: dynamic map state

`campaigns/{instance}/map_state.json` holds only what changes per session:

```json
{
  "mode": "exploration | combat",
  "room": "brewery_cellar",

  // Exploration mode
  "graph": {
    "nodes": [
      {"id": "tavern", "label": "Wizard's Tower Brewing Co.", "visited": true},
      {"id": "cellar", "label": "The Brewery Cellars", "visited": true},
      {"id": "ruins", "label": "Ancient Ruins", "visited": false}
    ],
    "edges": [
      {"from": "tavern", "to": "cellar"},
      {"from": "cellar", "to": "ruins"}
    ],
    "party_location": "cellar"
  },

  // Combat mode (no grid/terrain — those come from maps/{room_id}.json)
  "tokens": {
    "thork": {"x": 3, "y": 2, "hp": 7, "max_hp": 12, "conditions": [], "type": "party"},
    "rat_1": {"x": 8, "y": 5, "hp": 4, "max_hp": 7, "conditions": [], "type": "enemy"},
    "rat_2": {"x": 9, "y": 3, "hp": 0, "max_hp": 7, "conditions": ["dead"], "type": "enemy"}
  },
  "initiative": ["thork", "rat_1", "rat_2"],
  "current_turn": "rat_1",
  "round": 2
}
```

### What lives where

| Data | Location | Rationale |
|---|---|---|
| Party HP (ground truth) | `characters/{name}.md` | Bookkeeping agent owns this, unchanged |
| Party HP (combat snapshot) | `map_state.json` tokens | Convenience copy for single-file combat reference |
| Enemy HP | `map_state.json` tokens | Ephemeral — no other home |
| Enemy stat blocks | `encounters.md` | Static reference, unchanged |
| Token positions | `map_state.json` | Dynamic — changes per combat |
| Initiative order | `map_state.json` | Dynamic — tied to this scene |
| Location graph | `map_state.json` | Dynamic — built up as party explores |
| Room grid dimensions | `maps/{room_id}.json` | Static — same for all instances |
| Terrain and furniture | `maps/{room_id}.json` | Static — defined by campaign, not session |
| Campaign beat progress | `campaign_progress.md` | Bookkeeping agent owns this, unchanged |

### Flexibility

The DM agent is not required to populate every field. For a simple two-rat skirmish in a featureless room, bookkeeping may write only token positions and omit initiative — the frontend renders what it has. For a complex multi-room encounter, it writes the full schema.

Not every room needs a `maps/{room_id}.json`. If the file is absent, the frontend renders a plain grid with tokens only.

## Consequences
- **Enemy HP has a home.** It is not in `encounters.md` (static) or `campaign_progress.md` (too high-level). The map is the right place.
- **Party HP is duplicated during combat.** Acceptable: the map snapshot is a convenience copy. The bookkeeping agent is the source of truth for character files and also maintains the map snapshot. Both are written by bookkeeping after each turn.
- **Static terrain is authored once.** Campaign designers (or the DM at campaign creation) define room layouts in `maps/`. Bookkeeping never writes terrain — it only reads from it when the frontend needs to merge static + dynamic.
- **`map_state.json` is cleared at end of combat.** When bookkeeping writes `mode: "exploration"`, the tokens/initiative fields are dropped. The file returns to the exploration schema.
- **Constraint:** Do not put spell slots, inventory, or long-term character state in `map_state.json`. It is a scene-level document, not a character sheet.
- **Constraint:** Do not put dynamic state (token positions, HP) in `maps/{room_id}.json`. It is a static layout file, not a session tracker.
