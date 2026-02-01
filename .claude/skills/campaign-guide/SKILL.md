---
name: campaign-guide
description: Load and run D&D campaigns. Manages campaign instances, tracks story progression through Acts and Beats, presents pre-generated characters, and references campaign content (NPCs, locations). Use when starting campaigns or tracking campaign progress.
allowed-tools: Read, Write, Glob
---

# Campaign Guide

This skill enables you to load D&D campaigns from templates, create campaign instances, and track story progression.

## Campaign Structure

### Available Campaigns (Templates)
Campaign templates are stored in `available_campaigns/` at project root.

**Directory structure:**
```
available_campaigns/
└── [campaign_name]/
    ├── campaign_guide.md              # Story structure (Acts → Beats)
    ├── npcs.md                        # Important NPCs (optional)
    ├── locations.md                   # Key locations (optional)
    ├── encounters.md                  # Combat encounters & treasure (optional)
    └── pregenerated_characters/       # Ready-to-use characters (optional)
        ├── dwarf_fighter.md
        └── elf_wizard.md
```

### Expected Campaign Content

Each campaign folder should contain:

#### Required: campaign_guide.md
**Must include:**
- **Campaign Overview**: Level range, duration, themes, tone
- **Acts & Beats Structure**: Story progression with accomplishments
- **References**: Links to other campaign files (npcs.md, locations.md, etc.)
- **Agent Decision Points**: How to handle player choices
- **Branching Outcomes**: Success levels (complete/partial/minimal)

**For each Beat include:**
- Accomplishment (what players achieve)
- Agent Guidance (tips for running this beat)
- Branching options (player choices available)
- Key Elements (important story points)
- Atmospheric Details (sensory descriptions)

#### Optional: npcs.md
**Should include for each NPC:**
- Name and current role
- Motivation (what they want)
- Personality traits
- Physical description
- Speech patterns (how they talk)
- Available interactions (what players can do)
- Atmospheric details (mannerisms, body language)

#### Optional: locations.md
**Should include for each location:**
- Description (what it is)
- Visual details (what players see)
- Sensory elements (sounds, smells, temperature)
- Features (notable aspects)
- Story function (why it matters)

#### Optional: encounters.md
**Should include:**
- **Combat encounters**: Stats, tactics, quantity, difficulty
- **Puzzles/Traps**: Challenge description, solutions, consequences
- **Treasure**: Item descriptions, discovery context, effects
- **Balancing notes**: Adjustments for party size/level

#### Optional: pregenerated_characters/
**Each character file should include:**
- Character name, race, class, level
- Ability scores and combat stats
- Skills and proficiencies
- Equipment and treasure
- Class/racial features
- Character concept and personality
- Roleplaying notes

**Format:** Use same markdown structure as character-management skill templates

### Active Campaign Instances
When a campaign is started, create an instance in `campaigns/` directory:

```
campaigns/
└── [campaign_name]_[instance_name]/
    ├── campaign_guide.md              # Copied from template
    ├── npcs.md                        # Copied (can be modified)
    ├── locations.md                   # Copied
    ├── characters/                    # Party characters
    │   ├── character1.md
    │   └── character2.md
    ├── campaign_progress.md           # Tracks current Act/Beat
    └── sessions/
        ├── session_01.md
        └── session_02.md
```

---

## Listing Available Campaigns

Use Glob to find available campaigns:

```
Glob pattern="available_campaigns/*"
```

Then read each campaign's guide to get details:

```
Read file_path="available_campaigns/[campaign_name]/campaign_guide.md"
```

---

## Starting a Campaign Instance

### Step 1: Get Instance Name

Ask user: "What should we name this campaign instance?"
(e.g., "party1", "weekenders", "solo_run")

### Step 2: Create Instance Directory

Use Write to create the directory structure:

```
campaigns/[campaign_name]_[instance_name]/
```

### Step 3: Copy Campaign Files

Read from `available_campaigns/[campaign_name]/` and Write to instance:

1. **campaign_guide.md** - Copy story structure
2. **npcs.md** - Copy NPC details (if exists)
3. **locations.md** - Copy locations (if exists)

### Step 4: Create campaign_progress.md

Initialize progress tracking file:

```markdown
# [Campaign Name] - [Instance Name]

**Instance:** [instance_name]
**Template:** [campaign_name]
**Created:** [date]
**Last Session:** [date]
**Session Count:** 0

## Current Progress
- **Act:** 1
- **Beat:** 1.1 (starting beat name)
- **Status:** Not started

## Party
*(Characters will be added as they join)*

## Key Decisions
*(Track important player choices)*

## Next Session
*(Notes for next session)*
```

### Step 5: Create Subdirectories

- `campaigns/[name]_[instance]/characters/`
- `campaigns/[name]_[instance]/sessions/`

---

## Presenting Pre-generated Characters

When starting a campaign, check if pre-gens exist:

```
Glob pattern="available_campaigns/[campaign_name]/pregenerated_characters/*.md"
```

If found, present to players:

1. Read each pre-gen character file
2. Show summary: Name, Class, Race, Brief concept
3. Ask: "Would you like to use a pre-generated character or create your own?"

### Using a Pre-gen

If player chooses a pre-gen:

1. Read the pre-gen file
2. Write to `campaigns/[instance]/characters/[character_name].md`
3. Update `campaign_progress.md` to list character in Party section

### Creating Custom Character

If player wants custom character:
- Use the `character-management` skill
- Character will be created in `campaigns/[instance]/characters/`

---

## Tracking Campaign Progress

### Reading Current Progress

```
Read file_path="campaigns/[instance]/campaign_progress.md"
```

### Updating Progress

When story advances (beat completed, act finished):

1. Read current `campaign_progress.md`
2. Edit to update:
   - Current Act number
   - Current Beat number and name
   - Session count
   - Last played date
3. Add key decision to Key Decisions section
4. Update Next Session notes

### Acts and Beats

**Acts** = Major story phases (e.g., Act 1: Investigation, Act 2: Confrontation)
**Beats** = Individual accomplishments within an act

Format: `Beat X.Y (Beat Name)`
- Example: `Beat 1.2 (Into the Cellar)`
- Example: `Beat 2.1 (Journey to the Tower)`

---

## Session Management

### Creating Session Logs

After each game session, create a session log:

```
campaigns/[instance]/sessions/session_[number].md
```

**Session log template:**
```markdown
# Session [Number] - [Date]

## Attendance
- DM: [name]
- Players: [character names]

## Summary
[Brief summary of what happened]

## Key Events
- Event 1
- Event 2
- Event 3

## Combat Encounters
- [If any]

## Treasure/Rewards
- [Items found, XP gained]

## Story Progress
- **Completed Beats:** Beat X.Y (name)
- **Current Beat:** Beat X.Y (name)

## Notes for Next Session
- [Hooks, unresolved plot threads]
```

---

## Referencing Campaign Content

### NPCs

If campaign has `npcs.md`:

```
Read file_path="campaigns/[instance]/npcs.md"
```

Use for:
- NPC personalities and motivations
- Dialogue suggestions
- NPC stat blocks

### Locations

If campaign has `locations.md`:

```
Read file_path="campaigns/[instance]/locations.md"
```

Use for:
- Location descriptions
- Points of interest
- Maps and layouts

### Story Structure

Reference `campaign_guide.md` for:
- Act/Beat progression
- Story goals
- Branching paths
- Agent guidance (what to do if players go off-script)

---

## Example Workflow: Starting "A Most Potent Brew"

**User:** "I want to start A Most Potent Brew campaign"

**Agent Steps:**

1. **Check available campaigns:**
   ```
   Glob pattern="available_campaigns/*"
   Result: Found "a_most_potent_brew"
   ```

2. **Ask for instance name:**
   "What should we name this campaign instance?"
   User: "party1"

3. **Create instance:**
   ```
   campaigns/a_most_potent_brew_party1/
   ```

4. **Copy campaign files:**
   - Read `available_campaigns/a_most_potent_brew/campaign_guide.md`
   - Write to `campaigns/a_most_potent_brew_party1/campaign_guide.md`

5. **Initialize progress:**
   Create `campaign_progress.md` with:
   - Act: 1 (The Brewery Investigation)
   - Beat: 1.1 (The Job Offer)

6. **Check for pre-gens:**
   ```
   Glob pattern="available_campaigns/a_most_potent_brew/pregenerated_characters/*.md"
   Found: dwarf_fighter.md, elf_wizard.md
   ```

7. **Present characters:**
   "I found 2 pre-generated characters:
   - **Thork Ironforge** - Level 1 Dwarf Fighter (tank/melee)
   - **Elara Moonwhisper** - Level 1 Elf Wizard (spellcaster)

   Would you like to use one of these or create your own character?"

8. **Player chooses:**
   If Thork: Copy to `campaigns/a_most_potent_brew_party1/characters/thork.md`

9. **Ready to play:**
   "Campaign ready! You're starting Act 1, Beat 1.1: The Job Offer"

---

## Multiple Instances

You can run multiple instances of the same campaign:

```
campaigns/
├── a_most_potent_brew_party1/      # Monday group
├── a_most_potent_brew_weekenders/  # Weekend group
└── a_most_potent_brew_replay/      # Fresh replay
```

Each instance has:
- Independent characters
- Independent progress
- Independent sessions

---

## Campaign Progress Tips

### When to Advance Beats

Advance to next beat when:
- ✅ Beat's accomplishment achieved
- ✅ Story goal completed
- ✅ Players ready for next phase

### When to Advance Acts

Advance to next act when:
- ✅ All beats in current act completed
- ✅ Act's completion trigger met
- ✅ Major story milestone reached

### Tracking Decisions

Important player choices that affect story:
- Did they ally with or antagonize an NPC?
- Did they find the hidden treasure?
- Did they take the stealthy or direct approach?

Log these in `campaign_progress.md` → Key Decisions section.

---

## Integration with Other Skills

### character-management
Use for creating custom characters or modifying pre-gens.

### dnd-knowledge-store
Reference for:
- Class features mentioned in campaign
- Spell descriptions
- Monster stat blocks

---

## Troubleshooting

### "Campaign not found"
- Check `available_campaigns/` directory exists
- Verify campaign folder name matches

### "Instance already exists"
- Choose different instance name
- Or continue existing instance

### "No pre-generated characters"
- Not all campaigns have pre-gens
- Use character-management skill to create custom characters

---

## Summary

**Starting:** List campaigns → Create instance → Copy files → Initialize progress
**Playing:** Track progress → Log sessions → Reference content
**Characters:** Offer pre-gens OR custom creation
**Progress:** Acts → Beats → Key decisions

Campaign instances are independent, allowing multiple playthroughs of the same campaign with different parties and progress.
