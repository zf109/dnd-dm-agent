---
name: campaign-guide
description: Load and run D&D campaigns. Manages campaign instances, tracks story progression through Acts and Beats, presents pre-generated characters, and references campaign content (NPCs, locations). Use when starting campaigns or tracking campaign progress.
allowed-tools: Read, Write, Edit, Glob
---

# Campaign Guide

Load D&D campaigns from templates, create campaign instances, and track story progression.

---

## Quick Reference

### Campaign Structure & Content Format
See: **[campaign_structure.md](campaign_structure.md)**

- Template structure (available_campaigns/)
- Expected content (campaign_guide.md, npcs.md, locations.md, etc.)
- Instance structure (campaigns/[instance]/)
- Multiple instances support

### Starting Campaigns
See: **[starting_campaigns.md](starting_campaigns.md)**

- List available campaigns
- Create campaign instances
- Copy template files
- Present pre-generated characters
- Full workflow example

### Campaign Tracking (Loading & Playing)
See: **[campaign_tracking.md](campaign_tracking.md)**

- Load campaigns (find, read state, summarize)
- Log events during play
- Track progress (Acts & Beats)
- Reference campaign content
- Session workflow

---

## Core Concepts

### Templates vs Instances

**Templates** (`available_campaigns/[campaign]/`):
- Reusable campaign content
- Story structure, NPCs, locations, encounters
- Pre-generated characters (optional)

**Instances** (`campaigns/[campaign]_[instance]/`):
- Active playthroughs
- Independent state (progress, characters, log)
- Can diverge from template

### Acts and Beats

**Act** = Major story phase
**Beat** = Individual accomplishment within an act
**Format:** Beat X.Y (Beat Name)

Example:
- Act 1: Investigation
  - Beat 1.1: The Job Offer
  - Beat 1.2: Into the Cellar
  - Beat 1.3: Confronting the Villain

### State Files

**campaign_progress.md** - Current state snapshot:
- Current Act/Beat
- Party members
- Key decisions

**campaign_log.md** - Event history:
- Timestamped entries
- Character state changes, scene changes, story events

**campaign_guide.md** - Story structure:
- Acts and Beats with accomplishments
- Agent guidance
- Branching paths

**characters/*.md** - Party character files

---

## Typical Workflows

### Starting a New Campaign

1. List available campaigns: `Glob pattern="available_campaigns/*"`
2. Ask user for instance name
3. Create instance directory: `campaigns/[campaign]_[instance]/`
4. Copy template files (campaign_guide.md, npcs.md, etc.)
5. Initialize campaign_progress.md and campaign_log.md
6. Present pre-generated characters or create custom ones
7. Begin playing!

See [starting_campaigns.md](starting_campaigns.md) for details.

### Resuming a Campaign

1. User says: "Continue my [campaign] as [character]"
2. Find instance: `Glob pattern="campaigns/*/characters/[character].md"`
3. Load state: Read campaign_log.md, campaign_progress.md, character file
4. Summarize: Recent events, current situation, party status
5. Continue playing

See [campaign_tracking.md](campaign_tracking.md) for details.

### During Play

**As events happen:**
- Edit campaign_log.md to log key events (combat, decisions, state changes)
- Reference campaign files (npcs.md, locations.md, encounters.md)
- Update campaign_progress.md when story advances

**When beat completes:**
- Read campaign_guide.md for next beat
- Edit campaign_progress.md to advance
- Log completion in campaign_log.md

See [campaign_tracking.md](campaign_tracking.md) for details.

---

## Integration with Other Skills

**character-management:**
- Create and update characters
- Characters saved to `campaigns/[instance]/characters/`

**dnd-knowledge-store:**
- Reference D&D rules (classes, spells, monsters)
- Supplement campaign content

**dnd-dm:**
- Session techniques (narration, pacing, improvisation)
- Running encounters
- NPC roleplaying

---

## Summary

**Workflow:** List campaigns → Create instance → Present characters → Play → Log events → Track progress → Resume

**Tools:** Glob (find), Read (load), Write (create), Edit (update)

**Files:** Templates (reusable) → Instances (active state) → Characters (party)

For detailed instructions, see the reference files linked above.
