# ADR-017: Testing Philosophy

## Status
Accepted

## Context
This project has an unusual testing challenge: the core "business logic" lives in an AI agent guided by skill files in natural language, not in deterministic functions. Standard testing instincts — high coverage, mock external dependencies, fast CI — do not map cleanly onto a system where the unit of work is an LLM turn.

The codebase has accumulated several specific testing decisions (ADR-007 through ADR-010) without a document that explains the reasoning that connects them. This ADR records the philosophy so future contributors understand why the test suite is shaped the way it is, and what "enough testing" means here.

## Decision

### Principle 1: Match the test instrument to the failure mode

The dominant failure mode in this codebase is **agent correctness** — the bookkeeping agent reads state, reasons about it, and writes a result. The failure looks like: character HP is `9/12` when it should be `6/12`. No structural validator catches this. Only a test that knows the starting state, provides a synthetic event, and asserts the exact resulting value does.

The secondary failure mode is **interface regression** — a server endpoint, tool, or utility function returns the wrong value after a code change. This is a standard deterministic failure and is caught by standard unit tests.

These failure modes require different instruments:
- **Scenario evals** for agent correctness (real API, real files, known fixtures, exact assertions)
- **Unit tests** for deterministic code (no API, fast, broad coverage)

Do not use unit tests to test agent behaviour (they cannot catch the failure mode). Do not use evals to test endpoint logic (they are expensive and add no signal).

### Principle 2: Do not mock the agent or the file system in integration tests

From ADR-008: mocking the bookkeeping agent produces tests that pass when the real agent fails. The evals work because they run the real agent against real fixture files and assert real output. Substituting any part of that chain undermines the test.

Unit tests in `tests/` may mock file paths (via `tmp_path` fixtures) because they test parsing and HTTP logic, not agent decisions. Integration evals in `tests/integration/` use real files and make real API calls.

### Principle 3: TDD for deterministic code; fixture-first for agent behaviour

For deterministic code (endpoints, tools, utilities): write the failing test first, then the implementation. The test defines the contract. This applies to all new server endpoints and tool functions.

For agent-guided behaviour (bookkeeping checklist changes, new skill instructions): write or update the eval fixture and assertion first, then edit the skill. If the skill change is correct, the eval passes. If the eval cannot be written before the skill is edited, the spec is not clear enough yet.

This is TDD adapted to the project's architecture: the instrument changes, the discipline does not.

### Principle 4: Coverage is a signal, not a target

The current coverage is ~47% overall. This is expected and acceptable given the architecture:

| Module | Coverage | Why |
|--------|----------|-----|
| `tools/*.py` | 87–93% | Pure functions — unit tests are the right instrument, high coverage expected |
| `logging_config.py` | 96% | Configuration code — nearly fully covered |
| `server.py` | 46% | REST endpoints covered; WebSocket/session handler is agent-pipeline code, covered by evals |
| `claude_agent.py` | 29% | Agent orchestration — covered by evals, not by unit tests |
| `interactive.py` | 0% | CLI harness — not worth unit testing |

Do not chase coverage numbers on agent orchestration code. A unit test that reaches those lines without making a real API call tests nothing meaningful. The evals are the right instrument; they do not show up in coverage reports.

High coverage (85%+) is appropriate for pure-function modules. Low coverage on agent pipeline modules is expected — treat it as confirmation that the code is in the right layer, not as a gap to fill.

### Principle 5: No frontend unit tests; TypeScript is the safety net

The frontend renders SVG from a JSON payload. The rendering logic is visual — asserting that a token appears at pixel coordinates `(280, 360)` produces a test that is brittle, hard to read, and catches no real failure mode. The real failure modes are type errors (wrong field name, wrong shape) and missing data handling (null checks, empty arrays).

TypeScript compilation catches type errors. Manual browser verification catches visual regressions. These are sufficient.

Do not add React component tests (enzyme, testing-library) unless a specific, non-visual correctness property needs asserting (e.g. a calculation function extracted into a utility).

### Principle 6: Evolving the test suite with new features

Each type of new feature has a corresponding test obligation:

**New server endpoint or tool function:**
Add unit tests to `tests/`. Cover the happy path and key error paths (missing file, bad input, path traversal). Write the tests before the implementation.

**New bookkeeping capability** (new field written to a state file, new step in the checklist):
Add a new eval scenario to `tests/integration/test_bookkeeping_evals.py` with a corresponding fixture in `tests/fixtures/`. The scenario must:
1. Start from a known fixture state
2. Provide a synthetic DM exchange that triggers the new behaviour
3. Assert the exact value written to the file

This is the trigger: *if bookkeeping can now write a new file or a new field that affects game state, a new eval scenario is required.* The map state update (Step 4 added to the bookkeeping checklist on this branch) is an example of a capability that warrants eval coverage — see the known gap below.

**New skill that does not affect bookkeeping state** (e.g. a DM narration guide):
No new test required. The skill is narrative guidance; there is no file output to assert.

**New frontend component or rendering feature:**
TypeScript compilation and manual browser verification remain sufficient. No component tests.

**Feature spanning both layers** (e.g. new server endpoint + bookkeeping writes to a new file):
Both obligations apply: unit tests for the endpoint, eval scenario for the bookkeeping output.

### What level of testing is sufficient

A change is ready to merge when:

1. **New deterministic code** has unit tests covering its contract (happy path + key error paths). The test was written before the implementation.
2. **New bookkeeping capability** has a new eval scenario covering its output (see Principle 6).
3. **Changes to `campaign-guide` skill or bookkeeping pipeline** have passed the eval gate — all existing scenarios in `tests/integration/test_bookkeeping_evals.py` pass (ADR-010).
4. **TypeScript compiles clean** (`tsc --noEmit`).
5. **All existing tests pass** (`uv run pytest tests/ --ignore=tests/integration`).

Nothing else is required. In particular:
- No coverage percentage target
- No frontend component tests
- No CI pipeline (cost and API key management not yet justified at this scale — ADR-010)
- No end-to-end browser automation

## Consequences
- **The eval suite is the primary regression safety net for agent behaviour.** Its value is proportional to how realistic the fixtures are. When skills grow, update fixtures to match.
- **Unit test coverage on agent pipeline code will stay low.** This is correct, not a debt.
- **New contributors should expect two test patterns.** The split between `tests/` and `tests/integration/` reflects the two failure modes, not test importance. A passing eval on a bookkeeping change is stronger evidence than 100% unit coverage of the same change.
- **Constraint:** Do not add mocks for the bookkeeping agent or Claude SDK in integration tests. Do not add React component tests for visual rendering. Do not add a CI pipeline without first solving API key and cost attribution.
