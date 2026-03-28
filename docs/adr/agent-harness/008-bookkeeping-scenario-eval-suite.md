# ADR-008: Bookkeeping Scenario Eval Suite

## Status
Accepted

## Context
The bookkeeping subagent (ADR-006) runs with fresh context and `bypassPermissions` after every DM turn. It is guided by a skill checklist but there are no automated checks that it applied the right state transition — only that it ran without error.

The failure mode that matters is not structural invalidity (ADR-007 addressed this and rejected a bounds checker) but correctness: did the agent write the *right* value? A bookkeeping agent that reads a stale HP, applies correct arithmetic, and writes a valid but wrong result will silently corrupt game state across turns.

The existing integration test (`test_character_management_create_and_update_wizard`) exercises the main DM agent doing character edits inline. It does not test the bookkeeping subagent in isolation, nor does it test campaign progress tracking or beat advancement.

## Decision
A scenario eval suite in `tests/integration/` exercises `run_bookkeeping_subagent` directly with known fixture state and synthetic DM exchanges, then asserts the correct post-turn file state.

**Test structure per scenario:**
1. Copy fixture files to a temporary campaign directory
2. Call `run_bookkeeping_subagent(user_msg, dm_response, campaign, character)` directly
3. Read the resulting character/campaign files
4. Assert specific field values (not just structural validity)
5. Clean up the temporary directory

**Fixture files** live in `tests/fixtures/` as minimal but valid markdown character sheets and campaign progress files with known, controlled starting values. Fixtures are not copies of live campaign files — they are purpose-built for specific scenarios.

**Scenarios to cover:**

| Scenario | Starting state | Synthetic exchange | Assertion |
|----------|---------------|-------------------|-----------|
| HP damage | `HP: 10 / 12` | "Thork takes 3 damage" | character file contains `7 / 12` |
| HP healing | `HP: 5 / 12` | "Thork drinks a healing potion, regains 4 HP" | character file contains `9 / 12` |
| Spell slot use | `1st: total 2, used 0` | "Sapphire casts Magic Missile (1st level)" | spell slot used count is 1 |
| Beat advancement | Beat 1.1 in progress | "Party solved the rat problem" | `campaign_progress.md` shows Beat 1.2 or Act 1 complete |

**What evals do NOT assert:**
- Exact wording of the bookkeeping agent's output (it should produce no narration, but the test does not parse its text)
- Order of tool calls
- DM narration quality

These tests require `ANTHROPIC_API_KEY` and live in `tests/integration/` alongside the existing agent tests.

**Estimated runtime per scenario:**

Each scenario drives one full bookkeeping agent turn. The agent typically makes 4–6 tool calls: load the campaign-guide skill, read the character file, read `campaign_progress.md`, then one or two edits. At Sonnet-class latency (~2–4 s per API round-trip), a single scenario takes roughly **20–40 seconds**. The beat advancement scenario may take longer (~45–60 s) because it involves more file reads and potentially a more complex skill interaction.

| Scenario | Expected tool calls | Estimated time |
|----------|-------------------|----------------|
| HP damage | 4–5 | ~20–35 s |
| HP healing | 4–5 | ~20–35 s |
| Spell slot use | 5–6 | ~25–40 s |
| Beat advancement | 6–8 | ~40–60 s |
| **Full suite (sequential)** | | **~2–3 min** |

Scenarios are independent and can run in parallel (`pytest-asyncio` with `asyncio_mode = "auto"`) to bring wall-clock time down to the slowest single scenario (~45–60 s). API rate limits are unlikely to be a constraint at this scale.

These estimates assume no cold-start delay beyond normal SDK initialisation. If the campaign-guide skill is large, the first Skill tool call may take longer on the first run of a session.

**Estimated cost per scenario:**

Token accumulation is dominated by the campaign-guide skill (~4,000 tokens) re-appearing in every subsequent call's context. Output tokens are small — the agent produces mostly tool call parameters, not prose. Based on the current skill and fixture file sizes:

| Scenario | Est. input tokens | Est. output tokens | Est. cost (Sonnet) |
|----------|------------------|-------------------|-------------------|
| HP damage | ~20,000 | ~350 | ~$0.06 |
| HP healing | ~20,000 | ~350 | ~$0.06 |
| Spell slot use | ~23,000 | ~400 | ~$0.07 |
| Beat advancement | ~37,000 | ~500 | ~$0.11 |
| **Full suite** | | | **~$0.30** |

At roughly $0.30 per full suite run, cost is not a material constraint. Running the suite weekly during active development costs ~$1.50/month. Running it on every PR that touches the campaign-guide skill or bookkeeping pipeline adds ~$0.30 per PR.

These estimates assume Sonnet-class pricing (~$3/MTok input, ~$15/MTok output) and will shift if the campaign-guide skill grows significantly or if a more expensive model is used. The input cost scales roughly linearly with skill file size — doubling the skill doubles the per-scenario cost.

## Consequences
- **Correctness is tested end-to-end.** A scenario eval that passes confirms the full pipeline: skill checklist → file read → arithmetic → file write → correct value. A bounds check would have confirmed only the last property.
- **Regressions are caught.** If the campaign-guide skill's post-turn checklist is edited in a way that breaks HP tracking, the eval fails before it reaches a live session.
- **Fixtures are the source of truth for expected behaviour.** Adding a new scenario requires a fixture file and an assertion, not changes to production code.
- **Slow by design.** Each eval makes real API calls. They are not run in CI on every commit — they are run before merging changes to the campaign-guide skill or bookkeeping pipeline.
- **Constraint:** Do not mock the bookkeeping agent or the file system in these tests. The value comes from running the real agent against real files. Unit tests with mocks belong in `tests/` (not `tests/integration/`) and test parsing logic, not agent behaviour.
