# ADR-009: Bookkeeping Silence Check

## Status
Rejected

## Context
The bookkeeping subagent's system prompt instructs it to "Work silently using tools only" and explicitly forbids narration. This is enforced by prompt, not by code — nothing currently detects or flags a bookkeeping agent that starts producing conversational text.

A narrating bookkeeper is a latent failure mode. It indicates the agent is spending tokens on prose instead of tool use, is likely drifting from its checklist, and may be writing its reasoning to stdout rather than to the campaign files. It is also hard to notice in practice: the bookkeeping agent runs asynchronously after the DM response, its output is only visible in logs, and a short stray sentence won't obviously break anything while silently signalling a degraded agent.

Detection cannot be retroactive — by the time text output is observed, the bookkeeping turn has already completed. The check is therefore a monitoring signal, not a gate.

## Decision
Not implemented.

The implementation cost is near-zero — a string length check on messages already being processed, no extra API calls. But that makes the cost-benefit question moot: the real question is whether the check adds meaningful value, and it does not.

The check is warning-only and post-hoc. By the time a warning fires, the bookkeeping turn has already completed. A narrating bookkeeper may have still updated all files correctly — in which case the warning is noise. If it narrated *and* missed an update, the scenario evals (ADR-008) catch that on the next run. The silence check adds no earlier or more actionable signal than the evals already provide.

The 80-character threshold also introduces a concept that needs maintenance: future model versions may produce slightly more verbose tool confirmations that trip the threshold without indicating any real problem. Observability without a defined action to take when the signal fires adds noise, not value.

The right response to a narrating bookkeeper is to run the eval suite and check whether correctness was affected — not to log a warning and move on.

## Consequences
- **No silence check added.** The bookkeeping pipeline stays simpler with no threshold constant to tune.
- **Narration drift is covered indirectly.** If a narrating bookkeeper starts missing updates, the scenario evals (ADR-008) will catch the correctness failure.
- **Constraint:** Do not add a post-hoc text-length check as a substitute for correctness testing. If bookkeeper narration becomes an observed problem in practice, the right response is a new scenario eval that asserts the specific update was made, not a style-level warning.
