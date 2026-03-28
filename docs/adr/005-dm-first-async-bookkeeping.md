# ADR-005: DM Responds First, Bookkeeping Runs After

## Status
Accepted

## Context
Each player turn involves two concerns: (1) the DM narrating a response and (2) updating game state (character HP, spell slots, campaign progress, session log). These can be ordered as DM-first or bookkeeping-first, or run simultaneously.

The frontend uses a WebSocket per session (session ID generated on client, stored in sessionStorage) with one persistent `ClaudeSDKClient` per session to stream DM responses and tool events in real time.

## Decision
The DM agent responds to the player first. Once the DM response is complete, a separate bookkeeping subagent runs asynchronously on the same turn's context (player message + DM response).

The player sees the DM narration immediately. State updates happen in the background.

## Consequences
- **Responsive UX.** The player is never blocked waiting for bookkeeping to complete.
- **Eventual consistency.** State files reflect the *previous* turn's outcome, not the current one, until bookkeeping finishes. This is acceptable — the DM agent has the full conversation context and doesn't need persisted state to narrate correctly.
- **Bookkeeping has full context.** The handoff to the bookkeeping subagent includes both the player message and DM response, so nothing is lost.
- **WebSocket streaming aligns with this model.** Tool events (dice rolls, character updates) stream to the frontend as they happen, giving the player visibility into background state changes.
- **Constraint:** Do not block DM narration on bookkeeping completion. Do not make bookkeeping run before the DM responds. The ordering is intentional for UX reasons.
