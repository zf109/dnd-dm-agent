# ADR-015: Map Tool and Skill Design

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

## Decision

**Skill + built-in Write (Option A). ADR-001 is unchanged.**

Map state is written by the DM agent using the existing Write tool, following instructions in the map skill. The skill instructs the agent to Read back the file after writing to confirm the recorded state.

### Map skill

A new skill `.claude/skills/map/` guides the DM agent on:

- **When to use the map:** Use for any encounter with 3+ combatants, meaningful terrain, or when player positioning affects narrative outcomes. For trivial skirmishes (1-2 enemies, open space, resolved in 1-2 turns), a log note is sufficient. The goal is consistency and logical coherence — not bureaucratic tracking.
- **Exploration updates:** Write `map_state.json` with `mode: "exploration"` at scene transitions — entering a new room, discovering a new area. Build the graph from `locations.md`.
- **Combat lifecycle:** Write `mode: "combat"` on combat start (include all combatants and known terrain). Update positions and HP after each significant action. Write `mode: "exploration"` when combat ends (clears grid fields).
- **Confirmation:** After each Write, Read the file back to confirm the recorded state matches intent.
- **File location:** `campaigns/{instance}/map_state.json`

### State format
Defined in ADR-014. Only `mode` and `room` are required — all other fields are optional and populated at the DM's discretion.

## Consequences
- **ADR-001 unchanged.** No new Python tools. The bar for a custom tool remains: guaranteed atomic execution or external side effects (randomness, filesystem scaffolding). Map writes do not meet this bar.
- **Skill controls both judgment and mechanics.** The skill decides when to update and instructs how to do it — using the same Write/Read pattern as character-management.
- **No bookkeeping integration.** The bookkeeping subagent does not write to `map_state.json`. The DM agent owns map state entirely.
- **Constraint:** Do not add a custom tool for map updates in future unless a concrete failure mode emerges that skill + Write cannot handle. "It would be cleaner" is not sufficient justification.
