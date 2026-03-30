# ADR-015: Map Tool, Skill, and Bookkeeping Design

## Status
Accepted

## Context
ADR-001 limits custom MCP tools to two: `roll_dice` and `create_campaign_instance`. The justification was that anything not requiring guaranteed atomic execution or external side effects belongs in skills + built-in tools.

Three options for map updates were considered:

**A — Skill + built-in Write:** No new Python tool. The map skill instructs the DM agent to write `map_state.json` directly using the existing Write tool, then Read it back to confirm the state looks correct. Zero new infrastructure.

**B — Skill + `update_map` tool:** One new Python tool validates the JSON, writes the file, and returns a plain-text summary back to the agent. Two justifications were proposed: (1) malformed JSON silently breaks the frontend, and (2) the return value gives the agent confirmation without a separate Read.

**C — Skill + `set_scene` + `update_tokens`:** Two tools with separated responsibilities. Violates YAGNI.

Both justifications for option B were challenged:

1. **Malformed JSON** — LLMs write valid JSON reliably. The risk is low, and a Write + Read cycle catches any error anyway.
2. **Confirmation return** — a skill can instruct the agent to Read back what it wrote. The character-management skill does exactly this. No tool needed.

Neither justification holds. Option B is speculative complexity.

Option A was initially accepted — DM agent writes `map_state.json` directly. However, the same failure mode that motivated the bookkeeping subagent (ADR-006) applies here: the DM agent may not reliably update map state mid-session. The bookkeeping subagent exists precisely because the DM agent was unreliable at recording state changes.

The same logic that moved character updates and campaign progress to bookkeeping applies to the map:

> If DM agent knows spatial information (because it made decisions about token movement), that information is present in the DM's narrative. Bookkeeping already reads that narrative to extract HP changes — it can extract spatial changes the same way.

### Position inference: Option A vs Option B

Two approaches were considered for how bookkeeping extracts spatial (x/y) position data:

**Option A — Infer from relative narrative:** DM narrates naturally ("Thork charges north, now beside the barrel"). Bookkeeping interprets relative descriptions and infers approximate positions. Imprecise but sufficient when the grid is used for orientation rather than tactical adjudication.

**Option B — DM outputs a structured block:** DM narrates naturally for the player, then appends a machine-readable block (e.g. `<map_state>{...}</map_state>`) that the server strips before display. Bookkeeping extracts precise coordinates from the block. More accurate but requires server-side stripping and DM skill instructions for the format.

Option A is chosen as the pragmatic v1 approach. The combat grid in a narration-first AI DM game is primarily decorative — rough token placement that reinforces the narrative — not a tactical adjudicator. Option B is documented as the upgrade path if precise grid accuracy becomes a concrete player need.

## Decision

**Bookkeeping subagent owns `map_state.json`. ADR-001 is unchanged.**

Map state is written by the bookkeeping subagent, reading the DM's narrative to extract spatial and combat state changes — the same pattern used for character HP and campaign progress.

The map skill guides the DM agent on:
- When spatial context is worth surfacing (so it narrates it clearly)
- How to describe movement and positioning explicitly enough for bookkeeping to extract

### Map skill

A new skill `.claude/skills/map/` guides the DM agent on:

- **When to use the map:** Use for any encounter with 3+ combatants, meaningful terrain, or when player positioning affects narrative outcomes. For trivial skirmishes (1-2 enemies, open space, resolved in 1-2 turns), a log note is sufficient. The goal is consistency and logical coherence — not bureaucratic tracking.
- **Exploration narration:** When the party moves to a new location, name it clearly and describe connections to adjacent areas. Bookkeeping will update the graph from this.
- **Combat narration:** When tokens move, state direction and relative position explicitly — "Thork moves north, now flanking rat_1" rather than "Thork moves closer." Bookkeeping extracts positions from this.
- **File location:** `campaigns/{instance}/map_state.json`

### Bookkeeping subagent

The bookkeeping subagent's post-turn checklist (in the campaign-guide skill) is extended to include map state updates:

- **Exploration:** update `mode`, `room`, `graph.party_location`, mark newly visited nodes
- **Combat start:** write `mode: "combat"`, initialise tokens (HP from character files and encounter stat blocks, positions inferred from DM narrative), initiative order
- **Mid-combat:** update token HP, conditions, positions, `current_turn`, `round`
- **Combat end:** write `mode: "exploration"`, drop grid/tokens/initiative fields, restore graph

### State format
Defined in ADR-014. Only `mode` and `room` are required — all other fields are optional and populated at bookkeeping's discretion based on what the DM surfaced.

## Consequences
- **ADR-001 unchanged.** No new Python tools.
- **Bookkeeping owns map state.** Same agent, same pattern as character files and campaign progress. The DM agent does not write to `map_state.json`.
- **Map skill controls judgment, bookkeeping controls mechanics.** The skill decides when spatial context is worth narrating and instructs the DM how to narrate it clearly. Bookkeeping does the writing.
- **Positions are approximate.** Bookkeeping infers x/y from relative narrative descriptions. This is sufficient for orientation. Precise tactical grid coordinates require Option B (structured DM output block, server-side stripping) — implement if concrete need emerges.
- **Constraint:** Do not add a custom tool for map updates in future unless a concrete failure mode emerges that skill + bookkeeping cannot handle. "It would be cleaner" is not sufficient justification.
- **Constraint:** Do not implement Option B (structured map block) speculatively. The trigger is a player or DM complaint that grid positions are meaningfully wrong, not aesthetic preference for precision.
