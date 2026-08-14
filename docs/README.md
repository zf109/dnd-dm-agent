# docs

Index of documentation in this repo. Start with the top-level `CLAUDE.md` for commands and conventions; this file is for finding a specific decision or design doc.

## Architecture Decisions (`adr/`)

Core decisions, in number order:

- [001](adr/001-minimal-mcp-tools.md) — Minimal Custom MCP Tools
- [002](adr/002-markdown-state-persistence.md) — Markdown Files as State Persistence
- [003](adr/003-skill-based-capabilities.md) — Skill-Based Distributed Logic
- [004](adr/004-campaign-template-copy-on-create.md) — Campaign Instances as Full Copies of Templates
- [005](adr/005-dm-first-async-bookkeeping.md) — DM Responds First, Bookkeeping Runs After
- [006](adr/006-isolated-bookkeeping-subagent.md) — Bookkeeping as an Isolated Subagent with Fresh Context
- [017](adr/017-testing-philosophy.md) — Testing Philosophy

### `adr/agent-harness/` — the harness layer that validates and guards agent runtime behaviour

- [007](adr/agent-harness/007-character-data-integrity-validator.md) — Character Data Integrity Validator (rejected)
- [008](adr/agent-harness/008-bookkeeping-scenario-eval-suite.md) — Bookkeeping Scenario Eval Suite
- [009](adr/agent-harness/009-bookkeeping-silence-check.md) — Bookkeeping Silence Check (rejected)
- [010](adr/agent-harness/010-eval-regression-gate.md) — Eval Regression Gate

### `adr/session-management/` — session start, resume, and campaign browser flow

- [011](adr/session-management/011-session-management-and-resume.md) — Session Management and Campaign Resume Flow
- [012](adr/session-management/012-campaign-browser-frontend-design.md) — Campaign Browser Frontend Design

### `adr/map/` — map panel, state model, and DM narration integration

- [013](adr/map/013-map-panel-two-mode-architecture.md) — Map Panel Two-Mode Architecture
- [014](adr/map/014-map-state-model.md) — Map State Model
- [015](adr/map/015-map-tool-and-skill-design.md) — Map Tool, Skill, and Bookkeeping Design
- [016](adr/map/016-map-api-and-room-resolution.md) — Map API and Room Resolution

## Other docs

- [FRONTEND_PLAN.md](FRONTEND_PLAN.md) — Frontend architecture reference
- [mockups/](mockups/) — UI mockups (HTML/PNG) referenced by design ADRs
- [superpowers/](superpowers/) — Working plans and specs from past feature branches (not authoritative decisions — see the relevant ADR for the accepted design)
