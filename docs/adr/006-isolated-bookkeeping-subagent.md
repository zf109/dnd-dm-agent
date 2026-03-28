# ADR-006: Bookkeeping as an Isolated Subagent with Fresh Context

## Status
Accepted

## Context
State bookkeeping (updating character sheets, advancing campaign beats, writing session logs) could be handled by the main DM agent as part of its response, or by a persistent subagent that accumulates context, or by a lightweight subagent with fresh context each turn.

## Decision
Bookkeeping runs as a separate `ClaudeSDKClient` instance with:
- **Fresh context per turn** — no conversation history carried over from previous turns
- **`bypassPermissions` mode** — runs silently without prompting for file edit approvals
- **Restricted tool set** — only `Skill`, `Read`, `Write`, `Edit`, `Glob` (no dice, no campaign creation)
- **Domain logic delegated to skills** — the bookkeeping system prompt defers to `campaign-guide` skill for the post-turn checklist

The main DM agent uses `acceptEdits` permission mode and never uses `bypassPermissions`.

## Consequences
- **Clean separation of concerns.** Narration and bookkeeping are distinct responsibilities with distinct agents, prompts, and permissions.
- **Fresh context prevents drift.** The bookkeeping agent cannot be confused by earlier turns' narration accumulating in its context window.
- **`bypassPermissions` is scoped to bookkeeping only.** This is intentional — silent file writes are correct for bookkeeping, but would be unsafe for the interactive DM agent.
- **Checklist-driven.** Bookkeeping correctness is defined in the campaign-guide skill (the post-turn checklist), not in Python. Updating what gets tracked requires editing the skill, not the agent code.
- **Constraint:** Do not give the bookkeeping agent accumulated conversation history. Do not apply `bypassPermissions` to the main DM agent. Do not move the bookkeeping checklist logic into Python.
