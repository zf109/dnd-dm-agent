# Starting Campaigns

Step-by-step guide for creating campaign instances and presenting characters.

---

## Listing Available Campaigns

Use **Glob** to find available campaigns:

```
Glob pattern="available_campaigns/*"
```

Then read each campaign's guide to get details:

```
Read file_path="available_campaigns/[campaign_name]/campaign_guide.md"
```

Present to user:
- Campaign name
- Level range
- Brief description
- Theme/tone

---

## Creating a Campaign Instance

### Step 1: Get Instance Name

Ask user: "What should we name this campaign instance?"

**Examples:**
- "party1"
- "weekenders"
- "solo_run"
- "test_campaign"

**Instance naming:**
- Format: `[campaign_name]_[instance_name]`
- Example: `a_most_potent_brew_party1`

### Step 2: Create Instance Directory

Use **Write** to create the directory structure:

```
campaigns/[campaign_name]_[instance_name]/
```

### Step 3: Copy Campaign Files

Read from `available_campaigns/[campaign_name]/` and Write to instance directory.

**Files to copy:**

1. **campaign_guide.md** - Story structure (required)
2. **npcs.md** - NPC details (if exists)
3. **locations.md** - Location descriptions (if exists)
4. **encounters.md** - Encounters and treasure (if exists)

**Use Glob to check what exists:**
```
Glob pattern="available_campaigns/[campaign_name]/*.md"
```

### Step 4: Create campaign_progress.md

Initialize progress tracking file:

```markdown
# [Campaign Name] - [Instance Name]

**Instance:** [instance_name]
**Template:** [campaign_name]
**Created:** [YYYY-MM-DD]

## Current Progress
- **Act:** 1
- **Beat:** 1.1 (starting beat name)
- **Status:** Not started

## Party
*(Characters will be added as they join)*

## Key Decisions
*(Track important player choices)*
```

**Starting Beat:**
- Read campaign_guide.md to get Act 1, Beat 1 name
- Fill in the beat name in campaign_progress.md

### Step 5: Create campaign_log.md

Initialize event log:

```markdown
# [Campaign Name] - Event Log

**[YYYY-MM-DD HH:MM]** - Campaign instance created
```

### Step 6: Create Subdirectories

Create `characters/` directory:
```
campaigns/[campaign_name]_[instance_name]/characters/
```

### Step 7: Confirm Creation

Tell user:
```
Campaign instance '[campaign_name]_[instance_name]' created!

Location: campaigns/[campaign_name]_[instance_name]/
Starting at: Act 1, Beat 1.1 - [beat name]

Next: Choose or create your character.
```

---

## Presenting Pre-generated Characters

After creating the campaign instance, check if pre-gens exist.

### Step 1: Check for Pre-gens

Use **Glob**:
```
Glob pattern="available_campaigns/[campaign_name]/pregenerated_characters/*.md"
```

### Step 2: If Pre-gens Found

Read each pre-gen character file and extract:
- Character name
- Race
- Class
- Level
- Brief concept/personality

Present to player:
```
I found [X] pre-generated characters:

1. **[Name]** - Level [X] [Race] [Class]
   Concept: [brief description]

2. **[Name]** - Level [X] [Race] [Class]
   Concept: [brief description]

Would you like to use one of these or create your own character?
```

### Step 3a: Using a Pre-gen

If player chooses a pre-gen:

1. **Read** the pre-gen file from `available_campaigns/[campaign]/pregenerated_characters/`
2. **Write** to `campaigns/[instance]/characters/[character_name].md`
3. **Edit** campaign_progress.md to add character to Party section:
   ```markdown
   ## Party
   - [Character Name] ([Class] [Level])
   ```

### Step 3b: Creating Custom Character

If player wants custom character:

1. Use the **character-management skill**
2. Character will be created in `campaigns/[instance]/characters/`
3. Update campaign_progress.md Party section

### Step 4: Multiple Characters

If multiple players:
- Repeat pre-gen selection or character creation for each player
- Each character gets their own file in `characters/` directory
- All listed in campaign_progress.md Party section

---

## Example Workflow

**User:** "I want to start A Most Potent Brew campaign"

### Agent Steps:

**1. Confirm campaign exists:**
```
Glob pattern="available_campaigns/*"
→ Found: a_most_potent_brew
```

**2. Ask for instance name:**
```
Agent: "What should we name this campaign instance?"
User: "party1"
```

**3. Create instance directory:**
```
campaigns/a_most_potent_brew_party1/
```

**4. Copy campaign files:**
```
Read: available_campaigns/a_most_potent_brew/campaign_guide.md
Write: campaigns/a_most_potent_brew_party1/campaign_guide.md

Read: available_campaigns/a_most_potent_brew/npcs.md
Write: campaigns/a_most_potent_brew_party1/npcs.md

(repeat for locations.md, encounters.md if they exist)
```

**5. Initialize progress file:**
```
Write: campaigns/a_most_potent_brew_party1/campaign_progress.md

Content:
# A Most Potent Brew - party1
**Instance:** party1
**Template:** a_most_potent_brew
**Created:** 2026-02-07

## Current Progress
- **Act:** 1 (The Brewery Investigation)
- **Beat:** 1.1 (The Job Offer)
- **Status:** Not started

## Party
## Key Decisions
```

**6. Initialize log file:**
```
Write: campaigns/a_most_potent_brew_party1/campaign_log.md

Content:
# A Most Potent Brew - Event Log
**2026-02-07 15:30** - Campaign instance created
```

**7. Create characters directory:**
```
campaigns/a_most_potent_brew_party1/characters/
```

**8. Check for pre-gens:**
```
Glob pattern="available_campaigns/a_most_potent_brew/pregenerated_characters/*.md"
→ Found: dwarf_fighter.md, elf_wizard.md
```

**9. Present characters:**
```
Agent: "I found 2 pre-generated characters:

1. **Thork Ironforge** - Level 1 Dwarf Fighter
   Concept: Gruff ex-guard with a drinking problem

2. **Elara Moonwhisper** - Level 1 Elf Wizard
   Concept: Curious scholar seeking rare herbs

Would you like to use one of these or create your own character?"
```

**10. Player chooses:**
```
User: "I'll use Thork"

Agent:
- Reads: available_campaigns/a_most_potent_brew/pregenerated_characters/dwarf_fighter.md
- Writes: campaigns/a_most_potent_brew_party1/characters/thork.md
- Edits campaign_progress.md to add "- Thork Ironforge (Fighter 1)" to Party section
```

**11. Ready to play:**
```
Agent: "Campaign ready! You're starting Act 1, Beat 1.1: The Job Offer

Thork Ironforge (Fighter 1) - HP: 13/13

Let's begin..."
```

---

## Troubleshooting

### "Campaign not found"
- Check `available_campaigns/` directory exists
- Verify campaign folder name matches
- List available campaigns: `Glob pattern="available_campaigns/*"`

### "Instance already exists"
- Check if instance already created: `Glob pattern="campaigns/*"`
- Choose different instance name
- Or offer to continue existing instance (see campaign_continuity.md)

### "No pre-generated characters"
- Not all campaigns have pre-gens
- Proceed directly to custom character creation using character-management skill

### "Copy failed"
- Check if template files exist
- Verify read/write permissions
- Try copying files one at a time

---

## Integration

### With character-management skill
- Use for creating custom characters
- Characters saved to `campaigns/[instance]/characters/`

### With campaign_continuity.md
- After creation, see campaign_continuity.md for logging events
- For resuming campaigns later

### With tracking_progress.md
- Once playing, see tracking_progress.md for updating Act/Beat progress

---

## Summary

**Workflow:**
1. List campaigns → User chooses
2. Ask for instance name
3. Create instance directory
4. Copy campaign files from template
5. Initialize campaign_progress.md and campaign_log.md
6. Create characters/ directory
7. Present pre-gens or create custom characters
8. Update campaign_progress.md with party info
9. Begin playing!

**Tools used:**
- Glob (find campaigns, check for files)
- Read (read template files)
- Write (create instance files)
- Edit (update campaign_progress.md)
