# Campaign Structure

Directory structure and content format for campaign templates and instances.

---

## Available Campaigns (Templates)

Campaign templates are stored in `available_campaigns/` at project root.

### Directory Structure

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

---

## Expected Campaign Content

### Required: campaign_guide.md

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

### Optional: npcs.md

**Should include for each NPC:**
- Name and current role
- Motivation (what they want)
- Personality traits
- Physical description
- Speech patterns (how they talk)
- Available interactions (what players can do)
- Atmospheric details (mannerisms, body language)

### Optional: locations.md

**Should include for each location:**
- Description (what it is)
- Visual details (what players see)
- Sensory elements (sounds, smells, temperature)
- Features (notable aspects)
- Story function (why it matters)

### Optional: encounters.md

**Should include:**
- **Combat encounters**: Stats, tactics, quantity, difficulty
- **Puzzles/Traps**: Challenge description, solutions, consequences
- **Treasure**: Item descriptions, discovery context, effects
- **Balancing notes**: Adjustments for party size/level

### Optional: pregenerated_characters/

**Each character file should include:**
- Character name, race, class, level
- Ability scores and combat stats
- Skills and proficiencies
- Equipment and treasure
- Class/racial features
- Character concept and personality
- Roleplaying notes

**Format:** Use same markdown structure as character-management skill templates

---

## Active Campaign Instances

When a campaign is started, create an instance in `campaigns/` directory:

### Instance Directory Structure

```
campaigns/
└── [campaign_name]_[instance_name]/
    ├── campaign_guide.md              # Copied from template
    ├── npcs.md                        # Copied (can be modified)
    ├── locations.md                   # Copied
    ├── encounters.md                  # Copied (optional)
    ├── campaign_progress.md           # Tracks current Act/Beat
    ├── campaign_log.md                # Event log (session notes)
    └── characters/                    # Party characters
        ├── character1.md
        └── character2.md
```

### Instance Files

**campaign_progress.md** - Current state snapshot:
```markdown
# [Campaign Name] - [Instance Name]

**Instance:** [instance_name]
**Template:** [campaign_name]
**Created:** [date]

## Current Progress
- **Act:** 1
- **Beat:** 1.1 (starting beat name)
- **Status:** Not started

## Party
*(Characters will be added as they join)*

## Key Decisions
*(Track important player choices)*
```

**campaign_log.md** - Event log:
- See campaign_continuity.md for details
- Timestamped entries of key events
- Character state changes, scene changes, story progression

**characters/** - Party character files:
- Created using character-management skill
- Markdown format (.md files)
- One file per character

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
- Independent event log
- Separate campaign files (can be modified independently)

---

## Summary

**Templates** (`available_campaigns/`) = Reusable campaign content
**Instances** (`campaigns/`) = Active playthroughs with independent state

Each instance is a complete copy that can diverge from the template based on player choices.
