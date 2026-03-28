# ADR-001: Minimal Custom MCP Tools

## Status
Accepted

## Context
Claude Agent SDK supports custom tools via MCP servers. It would be natural to build custom tools for every domain operation: updating character HP, advancing campaign beats, looking up spells, managing inventory, etc.

## Decision
Expose only 2 custom MCP tools:
- `roll_dice` — dice mechanics require deterministic execution that the model cannot do reliably
- `create_campaign_instance` — filesystem scaffolding that requires atomic multi-file creation

Everything else (character CRUD, campaign state, D&D knowledge lookups, DM guidance) is handled via skills + built-in tools (Read, Write, Edit, Glob, Grep).

## Consequences
- **New capabilities go in skills, not tools.** Adding a skill is a markdown edit; adding a tool requires Python code, MCP server registration, and `allowed_tools` updates.
- **No custom tool for character updates.** The character-management skill defines patterns for using Write/Edit safely — this is intentional, not an omission.
- **Tool surface area stays minimal.** Fewer tools = simpler agent, less hallucination on tool selection, easier to reason about what the agent can do.
- **Constraint:** Anything requiring guaranteed atomic execution or external side effects (dice randomness, filesystem scaffolding) is the right candidate for a real tool. Everything else is not.
