# ADR-002: Markdown Files as State Persistence

## Status
Accepted

## Context
Game state (characters, campaign progress, session logs) needs to persist across turns and sessions. Common alternatives include SQLite, JSON with schemas, or in-memory state serialized to disk.

## Decision
All game state is stored as `.md` files in a structured directory layout:

```
campaigns/
  [instance]/
    characters/[name].md     # character sheets
    campaign_progress.md     # current Act/Beat
    campaign_log.md          # session history
```

Campaign story content (Acts, Beats, NPCs, locations) is also authored in markdown under `campaigns/available_campaigns/[template]/`.

## Consequences
- **Human-readable and git-diffable.** Players and DMs can inspect, edit, and version-control game state without tooling.
- **No schema migrations.** Adding a new field to a character sheet is a markdown edit, not a database migration.
- **Built-in tools work natively.** Read/Write/Edit/Grep operate directly on these files — no adapter layer needed.
- **No ACID guarantees.** Concurrent writes (e.g., if bookkeeping and DM agent both write simultaneously) could corrupt state. This is acceptable in a single-session, single-user context.
- **Constraint:** Do not move state into a database or structured JSON to "improve" it. The markdown format is load-bearing — it's what makes the built-in tool ecosystem work without custom persistence tooling.
- **Exception — structured spatial data:** State that is inherently coordinate-based (x/y positions, grid dimensions, terrain geometry) may use JSON. Markdown cannot express this cleanly and attempting to do so would make agent reads unreliable. The test: if the data would require parsing a table or custom syntax to extract numbers, JSON is the right format. Current JSON state files: `map_state.json` (dynamic combat/exploration state), `maps/{room_id}.json` (static room layout). All narrative state (character sheets, campaign progress, logs) remains markdown.
