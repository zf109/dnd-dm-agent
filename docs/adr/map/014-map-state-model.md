# ADR-014: Map State Model

## Status
Accepted

## Context
ADR-013 defines two map modes. This ADR defines what `map_state.json` contains and where each piece of game information lives.

Three models were considered:

**A — Thin map (positions only):** `map_state.json` stores spatial data only; HP and stats stay in existing character and encounter files. Simple, no duplication — but enemy HP has no natural home (encounters.md is static reference data, not mutable combat state), and the DM agent must cross-reference multiple files per turn.

**B — Combat notepad:** `map_state.json` is the DM's single combat reference: positions + current HP snapshot + initiative + conditions. Enemy HP lives here because it is ephemeral (rats die, encounter is over). Party HP is a snapshot from character files for convenience.

**C — Split map + combat tracker:** Two files with clear roles: `map_state.json` for spatial, `combat_state.json` for initiative/HP/conditions. Clean separation — but two files to update per action, and more complex skill instructions.

## Decision

Use **Model B — the combat notepad**. `map_state.json` is the DM's single reference during a scene, containing everything needed to understand the current spatial and combat situation.

### Schema

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

  // Combat mode
  "grid": {
    "width": 15,
    "height": 10
  },
  "terrain": [
    {"type": "wall", "x1": 6, "y1": 0, "x2": 6, "y2": 5}
  ],
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
| Party HP (combat snapshot) | `map_state.json` tokens | Convenience copy for DM to read in one place |
| Enemy HP | `map_state.json` tokens | Ephemeral — no other home |
| Enemy stat blocks | `encounters.md` | Static reference, unchanged |
| Token positions | `map_state.json` | Spatial layer |
| Initiative order | `map_state.json` | Tied to this scene |
| Location graph | `map_state.json` | Built from `locations.md` by DM skill |
| Campaign beat progress | `campaign_progress.md` | Bookkeeping agent owns this, unchanged |

### Flexibility

The DM agent is not required to populate every field. For a simple two-rat skirmish in a featureless room, the DM may write only token positions and omit terrain and initiative — the frontend renders what it has. For a complex multi-room encounter, it writes the full schema.

The skill (ADR-015) provides guidance on when detail is worth adding.

## Consequences
- **Enemy HP has a home.** It is not in `encounters.md` (static) or `campaign_progress.md` (too high-level). The map is the right place.
- **Party HP is duplicated during combat.** Acceptable: the map snapshot is a convenience copy. The bookkeeping agent is the source of truth for character files and also maintains the map snapshot. Both are written by bookkeeping after each turn.
- **`map_state.json` is cleared at end of combat.** When bookkeeping writes `mode: "exploration"`, the grid/tokens/initiative fields are dropped. The file returns to the exploration schema.
- **Constraint:** Do not put spell slots, inventory, or long-term character state in `map_state.json`. It is a scene-level document, not a character sheet.
