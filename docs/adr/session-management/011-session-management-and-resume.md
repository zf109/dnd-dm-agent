# ADR-011: Session Management and Campaign Resume Flow

## Status
Accepted

## Context
Players can currently start a new D&D session by selecting a campaign and character from dropdowns. Game state (character HP, spell slots, campaign progress, event log) is fully persisted on the server by the bookkeeping subagent after every turn. The campaign-guide skill already knows how to load and summarise prior state.

However, there is no meaningful way to return to an in-progress campaign:

- The session setup screen shows flat dropdowns with no indication of which campaigns are in progress, what beat they're on, or when they were last played.
- There is no distinction between resuming an existing instance and starting a fresh run of the same campaign.
- When a player reconnects to an existing campaign instance, the agent receives the same init message as a brand new session — it is not prompted to provide a "welcome back" recap.
- Chat history is stored only in `sessionStorage` (browser tab), so closing the tab loses the conversation, even though the underlying game state is intact on the server.

The result is that returning to a game requires remembering the exact campaign instance name, feels identical to starting fresh, and gives the player no orientation after a gap between sessions.

## Decision
Two changes address this without new backend infrastructure — all the data needed already exists in the campaign files.

### 1. Campaign browser (frontend)

Replace the flat campaign/character dropdowns with a **campaign browser**: a simple CRUD interface for campaign instances.

**Operations:**
- **Read** — list all in-progress campaign instances; click any to resume
- **Create** — select a template and start a new instance; the `create_campaign_instance` tool handles the filesystem scaffolding (ADR-004)
- **Delete** — remove an instance and its files
- **Update** — the game session itself; the bookkeeping subagent writes state after every turn. No separate UI action needed.

Each entry in the list shows enough to identify the campaign at a glance: campaign name, character, and current beat. No rich card metadata — the recap on resume provides the full orientation.

The existing `GET /api/campaigns` endpoint is extended to return this data. A new `DELETE /api/campaigns/{instance}` endpoint handles deletion.

### 2. Resume handshake (agent)

When a player resumes an existing instance, the frontend sends a different init message:

**New session (current behaviour):**
```
Session started. Campaign: '{campaign}'. Active character: '{character}'.
Please load the campaign via the campaign-guide skill at the start of the session.
```

**Resume:**
```
Resuming session. Campaign: '{campaign}'. Active character: '{character}'.
Use the campaign-guide skill to load current state and welcome the player back
with a brief recap of where they left off before asking what they'd like to do.
```

The campaign-guide skill already contains a "Loading a Campaign" section with instructions for producing a recap summary — no skill changes required.

The frontend distinguishes resume from new by whether the instance already exists on disk.

## Consequences
- **CRUD maps cleanly to the domain.** Create = new instance, Read = list + resume, Delete = remove instance, Update = gameplay. The absence of an explicit Update action is intentional — the game IS the update.
- **No new persistence infrastructure.** The list is built from existing campaign directories; deletion is a filesystem operation. No database, no session store.
- **Resume feels like a real return.** The player lands on a recap rather than a cold start, using the existing campaign-guide skill behaviour.
- **Chat history is still ephemeral.** Conversation text is not stored server-side — only game state. The recap replaces lost chat context. Full chat persistence is out of scope.
- **Constraint:** Do not store chat history server-side as part of this change. Do not modify the campaign-guide skill to support the resume flow — the existing "Loading a Campaign" section is sufficient. Do not merge campaign instance identity into the template structure (ADR-004 must be preserved).
