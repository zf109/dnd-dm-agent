---
name: map
description: Guides when and how to narrate spatial context. Use when the party moves to a new location or when combat involves positioning. Does not write files — bookkeeping handles map_state.json updates based on the DM's narrative.
allowed-tools: []
---

# Map Narration Guide

## When spatial context matters

- **Party enters a new room or area** → name it explicitly, mention visible connections to other areas
- **Combat with 3+ combatants or meaningful terrain** → describe starting positions and terrain features
- **Token moves** → state direction and relative position ("Thork moves north, now beside the barrel" not "Thork moves closer")
- **Skip map narration** for trivial skirmishes (1-2 enemies, open space, over in 1-2 turns) — log entry is enough

## Narration patterns for bookkeeping to extract

- **Location**: "The party enters the brewery cellars" → bookkeeping sets `room: "brewery_cellars"`
- **Movement**: "Thork charges north, ending up adjacent to rat_1" → bookkeeping infers position
- **Combat start**: "Initiative order: Thork (18), rat_1 (12), rat_2 (9)" → bookkeeping sets initiative
- **HP change**: already handled by character-management skill
- **Combat end**: "The last rat falls" → bookkeeping switches mode to exploration

## What the DM does not do

- Does not write `map_state.json`
- Does not state grid coordinates ("moves to 3,7") — relative narrative only
- Does not reference this skill mid-combat for every action — narrate naturally, bookkeeping extracts
