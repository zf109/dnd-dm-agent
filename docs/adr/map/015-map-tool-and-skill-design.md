# ADR-015: Map Tool and Skill Design

## Status
Accepted

## Context
ADR-001 limits custom MCP tools to two: `roll_dice` and `create_campaign_instance`. The justification was that anything not requiring guaranteed atomic execution or external side effects belongs in skills + built-in tools.

Three options for map updates were considered:

**A — Skill + built-in Write:** No new Python tool. The map skill instructs the DM agent to write `map_state.json` directly using the existing Write tool. Zero new infrastructure — but no JSON validation, meaning a malformed write silently corrupts the frontend.

**B — Skill + `update_map` tool:** One new Python tool validates the state dict, writes the file, and returns a plain-text summary of the current map state back to the agent. The skill governs when to use it.

**C — Skill + `set_scene` + `update_tokens`:** Two tools with separated responsibilities. More granular but violates YAGNI — one tool handles both scene initialisation and token updates with equal clarity.

## Decision

### Revise ADR-001: add `update_map` as the third custom tool

The justification for a real tool (rather than skill + Write):

1. **Structural integrity.** `map_state.json` is consumed by the frontend renderer. Malformed JSON or out-of-bounds coordinates silently break the UI. Unlike character markdown files (where a bad edit produces visible garbage text), a bad JSON write fails invisibly. Validation at the tool boundary is the right place to catch this.

2. **Agent confirmation.** The tool returns a plain-text summary of the recorded state (e.g. `"Combat mode. Room: cellar. Tokens: Thork(3,2 ❤7/12), Rat1(8,5 ❤4/7), Rat2(dead). Round 2, Rat1's turn."`). This lets the DM agent verify its own write without re-reading the file — important when updating positions mid-combat.

3. **Single call, full state.** The DM passes the complete desired state in one call, rather than a sequence of Write/Edit operations that could leave the file in a partial state mid-update.

### Tool signature

```python
def update_map(state: dict) -> str:
    """Write map_state.json for the current campaign instance.

    Args:
        state: Full map state dict matching the schema in ADR-014.
                Only 'mode' and 'room' are required; all other fields optional.

    Returns:
        Plain-text summary of the recorded state, or an error message.

    Example:
        update_map({
            "mode": "combat",
            "room": "brewery_cellar",
            "tokens": {"thork": {"x": 3, "y": 2, "hp": 7, "max_hp": 12, "conditions": [], "type": "party"}},
            "initiative": ["thork", "rat_1"],
            "current_turn": "thork",
            "round": 1
        })
        # Returns: "Combat mode. Room: brewery_cellar. Tokens: Thork(3,2 ❤7/12). Round 1, Thork's turn."
    """
```

The tool requires `campaign` to be passed as context (same pattern as other tools — the skill provides it from session context).

### Map skill

A new skill `.claude/skills/map/` guides the DM agent on:

- **When to use the map:** Use for any encounter with 3+ combatants, meaningful terrain, or when player positioning affects narrative outcomes. For trivial skirmishes (1-2 enemies, open space, resolved in 1-2 turns), a log note is sufficient.
- **Exploration updates:** Call `update_map` with `mode: "exploration"` at scene transitions — entering a new room, discovering a new area.
- **Combat lifecycle:** `mode: "combat"` on combat start (include all combatants and terrain). Update token positions and HP after each significant action. `mode: "exploration"` when combat ends (clears grid).
- **Flexibility:** The skill explicitly permits the DM to skip map updates for simple situations. Consistency and logical coherence of the narrative is the goal, not bureaucratic tracking.

## Consequences
- **ADR-001 revised from 2 to 3 tools.** The revised constraint: custom tools are justified only for operations requiring (a) guaranteed atomic execution, (b) external side effects (randomness, filesystem scaffolding), or (c) structural validation of data consumed directly by the frontend.
- **Skill controls judgment, tool controls correctness.** The skill decides when the map is worth updating; the tool ensures the update is valid when it happens.
- **No bookkeeping integration at this stage.** The bookkeeping subagent does not write to `map_state.json`. The DM agent owns map state. If HP gets out of sync between the map snapshot and the character file, the character file is authoritative.
- **Constraint:** Do not add a second map tool (e.g. separate `move_token`). The single `update_map` full-state replacement is intentionally simple — partial updates add complexity for minimal benefit at this scale.
- **Constraint:** The `update_map` tool must not be called by the bookkeeping subagent. Map state is DM-driven, not bookkeeping-driven.
