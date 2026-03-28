# ADR-007: Character Data Integrity Validator

## Status
Rejected

## Context
The bookkeeping subagent writes to character sheets and campaign progress files using unstructured markdown edits. Because it runs with `bypassPermissions` and fresh context each turn (ADR-006), there is no review step and no structural awareness — it knows what to write from the campaign-guide skill, but nothing prevents it from writing `HP: 15/12` or `Used: 3 / Total: 2`.

Two file types carry numeric invariants that can be silently violated:

- **Character files** (`campaigns/*/characters/*.md`): HP stored as `current / max` in a markdown table; spell slots stored as `total | used | remaining` per level
- **Campaign progress** (`campaigns/*/campaign_progress.md`): HP mirrored as `HP: current/max` inline

Violations compound across turns — a corrupted HP value in one turn is the starting point for the next.

## Decision
Not implemented.

The invariants under consideration (`current ≤ max` for HP, `used ≤ total` for spell slots) are small-number arithmetic on values that rarely exceed 20. The bookkeeping agent, guided by a structured skill checklist, handles this reliably. The added complexity of a parser, hook, and blocking logic is not justified by the actual failure rate.

More importantly, bounds checking catches the wrong failure mode. A validator confirming `3 ≤ 12` gives false confidence — it does not catch the more likely error where the agent applies damage to a stale HP value it misread, producing an internally valid but incorrect result (e.g. `6/12` written when it should be `9/12`). That class of error requires behavioural testing, not structural validation.

The higher-value harness investment is a scenario eval suite (ADR-008): fixture-based integration tests that assert the *correct* value was written after a known event, not merely a valid one.

## Consequences
- **No validator module added.** The codebase stays simpler; no new hook, no markdown parser.
- **Arithmetic correctness is covered by the scenario eval suite.** A test that starts at known HP and asserts the right post-damage value subsumes what a bounds check would have caught.
- **Structural corruption (agent edits wrong table cell) remains undetected at write time.** Accepted — this failure mode is rare and immediately obvious in play.
- **Constraint:** Do not add a bounds-check validator as a substitute for behavioural tests. If numeric drift becomes a real observed problem in practice, revisit with a focused eval test rather than a structural hook.
