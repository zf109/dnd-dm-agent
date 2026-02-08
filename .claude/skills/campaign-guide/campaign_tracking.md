# Campaign Tracking

Loading, playing, and tracking campaigns across sessions.

---

## Campaign State Files

```
campaigns/[instance]/
  ├── campaign_progress.md    # Current state: Act, Beat, Party, Key Decisions
  ├── campaign_log.md         # Event history (timestamped)
  ├── campaign_guide.md       # Story structure (Acts → Beats)
  ├── characters/*.md         # Party character files
  └── npcs.md, locations.md, encounters.md (optional reference files)
```

**campaign_progress.md** = Where we are now (snapshot)
**campaign_log.md** = How we got here (history)

---

## Loading a Campaign

When player says "continue my [campaign] as [character]":

### 1. Find Campaign Instance

```
Glob pattern="campaigns/*/characters/[character].md"
# or
Glob pattern="campaigns/*[campaign_name]*"
```

If multiple matches, ask user to clarify.

### 2. Load State

**Read:**
- `campaign_log.md` (last 10-20 entries)
- `campaign_progress.md` (current Act/Beat, Party, Decisions)
- `characters/[character].md` (HP, items, conditions)

### 3. Summarize

```
Welcome back! Last session (date):

Campaign: [Name] - [instance]
Act X, Beat X.Y - [Beat Name]

Recent Events:
- [event 1 from log]
- [event 2 from log]

Party Status:
- [Character]: HP, notable items/conditions

Current Situation: [where they are now]

What do you do?
```

---

## During Play: Logging Events

Use **Edit** to append to `campaign_log.md` immediately after key events occur.

### What to Log

**Character state changes:**
```markdown
**2026-02-07 15:42** - Combat: Goblin ambush
- Thorin took 8 damage (HP: 9/17)
- Elara used Magic Missile
- Found: 15 gold, short sword, 2 healing potions
```

**Scene changes:**
```markdown
**2026-02-07 15:50** - Arrived at Phandalin
- Took long rest (HP/slots restored)
```

**Story events:**
```markdown
**2026-02-07 16:00** - Met Sildar Hallwinter
- Agreed to find Gundren Rockseeker
- Learned about Redbrands
```

**Session boundaries:**
```markdown
**2026-02-07 18:00** - Session ended at tavern
- Planning to investigate manor tomorrow
```

### Format

```markdown
**[YYYY-MM-DD HH:MM]** - [Event Type]: [Description]
- [Detail 1]
- [Detail 2]
```

Be concise: 2-5 bullet points, specific details (names, numbers, locations).

**Log:** Combat outcomes, HP/item changes, scene changes, NPC interactions, key decisions
**Don't log:** Full dialogue, trivial actions, minor skill checks

---

## During Play: Tracking Progress

### Two Files to Maintain

**campaign_log.md** = Detailed event history (append-only)
**campaign_progress.md** = Current snapshot (update in place)

**CRITICAL: Update IMMEDIATELY after events occur.** Do not defer or batch updates. When something significant happens, update the files right away before continuing the narrative.

---

### Updating campaign_progress.md

#### 1. Party Status (Update After Character Changes)

When character HP, spell slots, items, or conditions change:

**Read** current Party section → **Edit** to reflect new state:

```markdown
## Party
- **Sapphire Star** (Level 1 Lightfoot Halfling Wizard) - Folk Hero background
  - HP: 1/8
  - Spell Slots: 1st level 0/2
  - Status: Exhausted (level 1), unconscious from combat
```

**Update when:**
- HP changes (damage, healing)
- Spell slots used/restored
- Conditions gained/removed (exhausted, poisoned, etc.)
- Major item changes (found magic item, lost weapon)
- Level ups

**Keep it concise:** Current HP/max, spell slots used/total, active conditions, notable items.

---

#### 2. Key Decisions (Update After Story Choices)

When players make story-significant decisions:

**Read** Key Decisions section → **Edit** to append under current beat:

```markdown
## Key Decisions

**Beat 1.1:**
- Accepted Glowkindle's quest for 50gp
- Chose to enter cellar alone without hiring help
- Agreed to resurrection deal with temple (owes quest in Thornwood)

**Beat 1.2:**
- Spared goblin scout (now potential ally)
- Chose stealth approach over direct combat
```

**What counts as key decision:**
- Quest acceptance/refusal
- Alliances or betrayals
- Major tactical choices
- Character commitments
- Story-altering actions

**One line per decision** - keep brief, capture essence.

---

#### 3. Current Progress (Update When Beat/Act Advances)

**Acts and Beats:**
- **Act** = Major story phase (e.g., Act 1: Investigation)
- **Beat** = Individual accomplishment (e.g., Beat 1.2: Into the Cellar)

**Advance Beat when:**
- Beat's accomplishment achieved (check campaign_guide.md)
- Story goal completed

**Advance Act when:**
- All beats in act completed
- Major milestone reached

**How to update:**

Edit `campaign_progress.md`:
```markdown
## Current Progress
- **Act:** Act 1: Investigation
- **Beat:** Beat 1.3: Confronting Villain  # ← Updated
```

Then log the advancement in `campaign_log.md`:
```markdown
**2026-02-07 16:15** - Completed Beat 1.2, advancing to 1.3
- Cleared cellar, found evidence
```

---

## Referencing Campaign Content

During play, read these files as needed:

- **campaign_guide.md** - Story structure, beat accomplishments, branching paths
- **npcs.md** - NPC details, motivations, speech patterns
- **locations.md** - Location descriptions, atmosphere
- **encounters.md** - Combat stats, puzzles, treasure

---

## Session Workflow

**Start:**
1. Load campaign (find, read files, summarize)
2. Check current beat in campaign_progress.md
3. Read beat details from campaign_guide.md

**During:**
- Reference npcs.md, locations.md, encounters.md as needed
- Log key events to campaign_log.md
- Update campaign_progress.md when beat/act advances

**End:**
- Log session end in campaign_log.md
- Update "Last Played" date in campaign_progress.md

---

## Quick Reference

**Tools:**
- Glob (find campaigns)
- Read (load state, reference files)
- Edit (log events, update progress)

**Files:**
- campaign_progress.md = current state
- campaign_log.md = event history
- campaign_guide.md = story structure
- characters/ = party state

**Lifecycle:**
Load → Play → Log → Update → Resume
