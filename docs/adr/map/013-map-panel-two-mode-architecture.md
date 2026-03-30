# ADR-013: Map Panel Two-Mode Architecture

## Status
Accepted

## Context
The frontend has a `MapPlaceholder` component in the top panel of the main view. It needs to serve two distinct purposes during a session:

1. **Orientation during exploration** — the player moves through named locations (Tavern → Cellar → Ruins). A spatial display helps them understand where they are and what's connected.
2. **Tactical positioning during combat** — when a fight starts, position matters: which enemy is adjacent, who has line of sight, which way to retreat.

These are not separate features — they are the same panel at different levels of zoom and detail. A human DM uses the same battle mat for both: room sketch for navigation, grid overlay for fights.

## Decision

The map panel operates in two modes, switching when the DM agent decides:

### Exploration mode
- Renders a **location graph**: named nodes (rooms/areas) connected by edges (passages/doors)
- The party position is a single dot on one node
- Graph is defined by the campaign's `locations.md` and initialised when the DM sets the scene
- No grid, no individual token positions

### Combat mode
- Renders a **tactical grid**: fixed-size cells overlaid on the current room
- Each entity (party members, enemies, environmental hazards) is a token with x/y coordinates
- Current HP and conditions shown on token hover
- Terrain (walls, doors, obstacles) rendered as visual barriers

### Mode switching
The DM agent switches modes explicitly via the `update_map` tool (ADR-015). There is no automatic mode detection. The DM decides when spatial positioning is meaningful enough to warrant the grid — for a trivial skirmish it may never switch to combat mode.

### Unified state file
Both modes share a single `map_state.json` in the campaign instance directory. The `mode` field controls which view the frontend renders. This means the frontend never needs to know which mode to show — it always reads the same file.

## Consequences
- **Agent-driven, not system-driven.** The map updates when the DM agent reaches for the tool, not on automatic triggers. Simple combats may never use combat mode.
- **One component, two views.** The frontend `MapPanel` component renders conditionally based on `mode`. No separate exploration vs. combat components.
- **Flexible fidelity.** The DM can provide a rough location graph from `locations.md` immediately, and add grid detail only when a fight needs it.
- **Constraint:** Do not auto-switch modes based on narrative keywords ("combat started", etc.). Mode transitions are always explicit tool calls.
- **Constraint:** Do not require a map update on every turn. The map is a tool the DM reaches for when spatial context is useful, not a mandatory bookkeeping step.
