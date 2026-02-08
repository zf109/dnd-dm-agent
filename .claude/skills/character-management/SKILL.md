---
name: character-management
description: Manage D&D 5e characters using markdown files. Create, read, update characters with Write/Read/Edit tools. Provides character templates, edit patterns, and validation rules. Use when players create characters, level up, take damage, or update character information.
allowed-tools: Read, Write, Edit
---

# Character Management

This skill enables you to manage D&D 5e characters using markdown files and built-in file tools (Read, Write, Edit).

## Quick Reference

| Action | Tools Used | Files to Reference |
|--------|-----------|-------------------|
| **Create character** | Write | [character_template.md](character_template.md), [character_example.md](character_example.md) |
| **Get character** | Read | - |
| **Update character** | Read + Edit | [edit_examples.md](edit_examples.md) |
| **Validate character** | Read | [validation_rules.md](validation_rules.md) |

## Character File Location

All character files are stored as markdown:
```
campaigns/[campaign_instance]/characters/[character_name].md
```

**Example:**
```
campaigns/a_most_potent_brew_party1/characters/thork.md
campaigns/a_most_potent_brew_party1/characters/elara.md
```

---

## Creating Characters

### Step 1: Understand the Template

Reference [character_template.md](character_template.md) for the complete structure.

See [character_example.md](character_example.md) for a fully filled-out example (Thork Ironforge, Level 1 Dwarf Fighter).

### Step 2: Gather Character Information

You need (minimum):
- Character name
- Class and level
- Race
- Ability scores (STR, DEX, CON, INT, WIS, CHA)
- Background (optional but recommended)

### Step 3: Use Write Tool

```
Write(
  file_path="campaigns/[instance]/characters/[name].md",
  content=[filled-out template based on character_template.md]
)
```

**Example:**
```
Write(
  file_path="campaigns/a_most_potent_brew_party1/characters/thork.md",
  content="# Thork Ironforge - Level 1 Dwarf Fighter\n\n..."
)
```

### Step 4: Validate

After creating:
1. Read the character file
2. Check against [validation_rules.md](validation_rules.md)
3. Fix any issues found
4. Re-check until character is valid

---

## Reading Characters

Use the Read tool:

```
Read(file_path="campaigns/[instance]/characters/[name].md")
```

**When to read:**
- Player asks about their character
- Before making updates (always read first!)
- To check current HP, abilities, equipment
- During combat to reference stats

---

## Updating Characters

### Safe Update Process

1. **Read the character file** (required before editing)
2. **Identify the specific section** to change
3. **Use Edit tool** with exact old_string/new_string
4. **Validate after editing** to check for errors
5. **Fix any validation errors** and repeat

### Common Updates

Reference [edit_examples.md](edit_examples.md) for detailed patterns. Key examples:

#### Taking Damage
```
old_string: "| **Hit Points** | 12 / 12 | Hit Die: d10 |"
new_string: "| **Hit Points** | 7 / 12 | Hit Die: d10 |"
```

#### Healing
```
old_string: "| **Hit Points** | 7 / 12 | Hit Die: d10 |"
new_string: "| **Hit Points** | 12 / 12 | Hit Die: d10 |"
```

#### Level Up (requires multiple edits)
- Update class & level
- Update XP
- Update HP and Hit Dice
- Add new class features

#### Adding Equipment
Update both weapons table and equipment list.

#### Spending Currency
Check current amount first, then update if sufficient.

#### Notes and Campaign Updates
Append to notes section with new information.

### Edit Best Practices

✅ **DO:**
- Read before editing
- Edit specific sections only
- Validate after changes
- Use exact string matching

❌ **DON'T:**
- Edit without reading first
- Replace entire file for small changes
- Skip validation
- Allow invalid values (negative HP, etc.)

---

## Validation

### When to Validate

- ✅ After creating a new character
- ✅ After level up
- ✅ After major stat changes
- ✅ After equipment changes
- ✅ Before starting an adventure

### How to Validate

To validate a character:

1. **Read the character file** using the Read tool
2. **Check against [validation_rules.md](validation_rules.md)**
3. **Verify all required fields** are present:
   - Character name, class, level, race
   - All 6 ability scores
   - HP (current/max), AC, hit dice
4. **Check D&D rules**:
   - HP: 0 ≤ current ≤ max
   - Ability scores: typically 8-20
   - Proficiency bonus matches level
   - Class features match level
5. **Report any issues** found

### Validation Rules

See [validation_rules.md](validation_rules.md) for complete rules. Key checks:

- **HP:** Must be between 0 and maximum
- **Ability Scores:** Typically 8-20 (1-30 absolute range)
- **Currency:** Cannot be negative
- **Hit Dice:** Used ≤ Total
- **Level Features:** Must have all class features for level
- **Proficiency Bonus:** Must match level
- **Spell Slots:** Used ≤ Total

---

## Character Creation Walkthrough

### Full Example: Creating a Level 1 Fighter

**User request:** "Create a dwarf fighter named Thork"

**Step 1: Consult dnd-knowledge-store skill for class/race details**
```
Use Skill: dnd-knowledge-store
Search for Fighter and Dwarf information
```

**Step 2: Determine stats**
- Use standard array [15, 14, 13, 12, 10, 8]
- Fighter needs high STR/CON
- Dwarf gets +2 CON, +2 STR (Mountain Dwarf)
- Final: STR 16, DEX 14, CON 15, INT 10, WIS 12, CHA 8

**Step 3: Calculate derived stats**
- HP = 10 (Fighter d10) + 2 (CON mod) = 12
- AC = 16 (chain mail armor)
- Proficiency bonus = +2 (level 1)

**Step 4: Choose Fighting Style**
- Options: Archery, Defense, Dueling, Great Weapon Fighting, Protection, Two-Weapon Fighting
- Choose: Defense (+1 AC while wearing armor)

**Step 5: Write character file**
```
Write(
  file_path="campaigns/a_most_potent_brew_party1/characters/thork.md",
  content=[Use character_template.md and fill in all values]
)
```

**Step 6: Validate**
1. Read the created character file
2. Check against [validation_rules.md](validation_rules.md)
3. Verify all required fields are present and valid

**Step 7: Fix any errors and re-check**

---

## Character Management Workflows

### Combat Workflow

1. **Player declares action** → "I attack with my longsword"
2. **Roll attack** → Use roll_dice tool: "1d20+5"
3. **If hit, roll damage** → Use roll_dice tool: "1d8+3"
4. **Update enemy/character HP** → Use Edit tool

### Rest Workflow

#### Short Rest
- Spend Hit Dice to heal
- Restore short rest abilities (Second Wind, etc.)
- Update character file with Edit tool

#### Long Rest
- Restore all HP
- Restore half of Hit Dice (minimum 1)
- Restore all long rest abilities
- Restore all spell slots

### Level Up Workflow

1. **Check XP threshold**
2. **Calculate new HP** → Roll hit die + CON mod
3. **Update level**
4. **Add new class features** (reference dnd-knowledge-store)
5. **Update proficiency bonus** if applicable
6. **Update spell slots** if caster
7. **Validate character**

### Inventory Management

- **Add items:** Edit equipment section
- **Remove items:** Edit equipment section
- **Update currency:** Add/subtract from currency section
- **Update weapons:** Edit weapons table

---

## Tips for Character Management

1. **Always read before editing** - Required by Edit tool
2. **Reference the example** - [character_example.md](character_example.md) shows proper formatting
3. **Use edit patterns** - [edit_examples.md](edit_examples.md) has safe patterns
4. **Validate frequently** - Catch errors early
5. **Check D&D rules** - Use dnd-knowledge-store skill for class/race details
6. **Be specific with edits** - Edit only what changed
7. **Handle edge cases** - HP can't go below 0 or above max

---

## Integration with Other Tools

### roll_dice Tool
Use for all dice rolls:
- Attack rolls
- Damage rolls
- Ability checks
- Saving throws
- Hit point rolls on level up

### dnd-knowledge-store Skill
Reference for:
- Class features by level
- Racial traits
- Spell descriptions
- Equipment stats

### create_campaign_instance Tool
Creates campaign instance directory where characters are stored.

---

## Troubleshooting

### Problem: "File not found"
**Solution:** Ensure campaign instance exists and character name is correct. Path format: `campaigns/[instance]/characters/[name].md`

### Problem: "Edit failed - old_string not found"
**Solution:** Read the file first. Ensure old_string matches exactly (including spacing/formatting).

### Problem: "HP is negative"
**Solution:** HP minimum is 0. Character is unconscious, not dead (death is at failed death saves).

### Problem: "Character has wrong features for level"
**Solution:** Reference dnd-knowledge-store for correct class features at that level.

---

## Summary

**Creating:** Write + character_template.md + Read (to verify)
**Reading:** Read
**Updating:** Read + Edit + edit_examples.md
**Validating:** Read character + check against validation_rules.md

**Key principle:** Markdown files + built-in tools (Read/Write/Edit) = complete character management system

No custom create/update/validate tools needed! The combination of markdown files and built-in tools provides everything necessary for robust D&D character management.
