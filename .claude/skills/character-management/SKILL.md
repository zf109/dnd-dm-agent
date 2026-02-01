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
| **Validate character** | validate_character tool | [validation_rules.md](validation_rules.md) |

## Character File Location

All character files are stored as markdown:
```
game_sessions/[session_name]/characters/[character_name].md
```

**Example:**
```
game_sessions/test_session/characters/thork.md
game_sessions/test_session/characters/elara.md
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
  file_path="game_sessions/[session]/characters/[name].md",
  content=[filled-out template based on character_template.md]
)
```

**Example:**
```
Write(
  file_path="game_sessions/session1/characters/thork.md",
  content="# Thork Ironforge - Level 1 Dwarf Fighter\n\n..."
)
```

### Step 4: Validate

After creating:
```
validate_character(session_name="session1", character_name="thork")
```

Fix any errors reported, then validate again until character is valid.

---

## Reading Characters

Use the Read tool:

```
Read(file_path="game_sessions/[session]/characters/[name].md")
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

Use the `validate_character` tool:

```
validate_character(
  session_name="session1",
  character_name="thork"
)
```

### Understanding Validation Output

**Valid character:**
```json
{
  "valid": true,
  "message": "Character is ready for adventure!"
}
```

**Invalid character:**
```json
{
  "valid": false,
  "errors": [
    "HP cannot be negative (current: -5)",
    "Missing required field: Character class"
  ],
  "warnings": [
    "AC seems low for a Fighter"
  ]
}
```

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
  file_path="game_sessions/session1/characters/thork.md",
  content=[Use character_template.md and fill in all values]
)
```

**Step 6: Validate**
```
validate_character(session_name="session1", character_name="thork")
```

**Step 7: Fix any errors and re-validate**

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

### validate_character Tool
Use after character modifications to ensure D&D 5e compliance.

### dnd-knowledge-store Skill
Reference for:
- Class features by level
- Racial traits
- Spell descriptions
- Equipment stats

### create_game_session Tool
Creates session directory where characters are stored.

---

## Troubleshooting

### Problem: "File not found"
**Solution:** Ensure session exists and character name is correct. Path format: `game_sessions/[session]/characters/[name].md`

### Problem: "Edit failed - old_string not found"
**Solution:** Read the file first. Ensure old_string matches exactly (including spacing/formatting).

### Problem: "Validation failed - HP negative"
**Solution:** HP minimum is 0. Character is unconscious, not dead (death is at failed death saves).

### Problem: "Character has wrong features for level"
**Solution:** Reference dnd-knowledge-store for correct class features at that level.

---

## Summary

**Creating:** Write + character_template.md + validate
**Reading:** Read
**Updating:** Read + Edit + edit_examples.md + validate
**Validating:** validate_character tool + validation_rules.md

**Key principle:** Markdown files + built-in tools + validation = complete character management system

No custom create/update tools needed! The combination of skills and built-in tools provides everything necessary for robust D&D character management.
