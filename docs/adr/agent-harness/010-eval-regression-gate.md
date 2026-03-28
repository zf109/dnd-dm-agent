# ADR-010: Eval Regression Gate

## Status
Accepted

## Context
The scenario eval suite (ADR-008) exists but has no enforced trigger — it runs when someone remembers to run it. This makes it easy to skip when it matters most: immediately before merging a change to the campaign-guide skill or the bookkeeping pipeline.

The evals are slow (~2–3 min) and cost real money (~$0.30 per run), so they should not run on every commit. But without a defined gate, "run before merging" remains informal and will be missed under time pressure.

## Decision
The eval suite is a **required gate** for two change categories:

| Change category | Gate |
|----------------|------|
| Any edit to `.claude/skills/campaign-guide/` | Run eval suite before merging |
| Any edit to `run_bookkeeping_subagent` or `get_bookkeeping_options` in `claude_agent.py` | Run eval suite before merging |

All other changes (DM agent prompt, other skills, tooling, tests) do not require the gate.

**Enforcement mechanism:** The ADR compliance reviewer hook (PostToolUse agent hook on Write/Edit in `.claude/settings.json`) reads all ADRs after every file modification. When a gated file is edited, the reviewer cites this ADR and its output surfaces as a `systemMessage` back to the Claude Code session that made the change. Claude Code is then responsible for running the eval suite and confirming all 4 scenarios pass before completing the task.

This is a Claude Code gate, not a human one. The trigger is automatic (fires on every relevant Write/Edit) and the agent doing the work receives the prompt immediately in the same session.

The gate is not automated in CI. The cost and latency of running LLM evals on every PR is not justified at this scale.

**How to run:**
```bash
uv run pytest tests/integration/test_bookkeeping_evals.py -v
```

All 4 scenarios must pass. A single failure blocks the merge.

## Consequences
- **The gate is as strong as the ADR compliance reviewer.** It relies on the reviewer hook firing correctly and Claude Code acting on the `systemMessage`. This is the same mechanism that enforces all other ADR constraints in this codebase — if the reviewer is working, the gate is working.
- **False negatives are possible.** A change to a skill file that does not affect bookkeeping will still trigger the gate. This is acceptable; a ~3 min run is a low cost for the confidence.
- **Gate scope is narrow by design.** Requiring evals for every change would make them feel like a burden and encourage skipping. Scoping to the two change categories keeps the gate meaningful.
- **Constraint:** Do not add the eval suite to a CI pipeline without also solving the API key management and cost attribution problems first. Do not widen the gate to cover all changes — this defeats the purpose of a targeted regression check.
