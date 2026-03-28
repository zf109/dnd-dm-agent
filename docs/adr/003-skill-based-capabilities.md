# ADR-003: Skill-Based Distributed Logic

## Status
Accepted

## Context
Domain logic (D&D rules, character templates, campaign structure, DM techniques) needs to be accessible to the agent. Options include: embedding it in the system prompt, building it into Python tools, storing it in a vector database (RAG), or using the Claude Code skills system.

## Decision
All domain knowledge and capability patterns are factored into `.claude/skills/`:

- `dnd-knowledge-store/` — D&D 5e rules, spells, monsters, class features
- `character-management/` — character templates, edit patterns, validation rules
- `campaign-guide/` — campaign loading, Acts/Beats tracking, post-turn bookkeeping checklist
- `dnd-dm/` — DM narration techniques, pacing, improvisation guidance

Skills are loaded on demand via the `Skill` tool and declare their own `allowed_tools`.

## Consequences
- **Adding knowledge requires no code changes.** New monsters, spells, or DM guidance is a markdown edit to a skill file.
- **Skills are independently testable.** Each skill can be invoked in isolation without running the full agent.
- **No RAG infrastructure.** The skills system avoids the complexity of embedding pipelines, vector stores, and retrieval tuning. Skills are loaded in full when invoked.
- **Skills compose with built-in tools.** The character-management skill uses Write/Edit directly — no custom tool wrapper needed.
- **Constraint:** Do not move skill content into the system prompt (bloats every conversation) or into Python (breaks the no-code-for-knowledge principle). If a capability can be expressed as a skill, it should be.
