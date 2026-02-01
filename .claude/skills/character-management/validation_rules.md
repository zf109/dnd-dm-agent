# Character Validation Rules

This document explains what the `validate_character` tool checks when validating a D&D 5e character.

## Required Fields

Every character must have these fields filled in:

### Basic Information
- ✅ Character Name
- ✅ Class
- ✅ Level (must be 1-20)
- ✅ Race

### Ability Scores
- ✅ All six ability scores (STR, DEX, CON, INT, WIS, CHA)
- ✅ Ability scores must be between 1-30 (typically 8-20 for level 1-19)

### Combat Stats
- ✅ Armor Class (AC)
- ✅ Hit Points (current and maximum)
- ✅ Hit Dice
- ✅ Speed

## Validation Rules

### 1. Hit Points
```
✅ Valid:
- HP: 12 / 12  (current ≤ maximum)
- HP: 0 / 12   (unconscious but valid)

❌ Invalid:
- HP: -5 / 12  (negative HP not allowed)
- HP: 15 / 12  (current > maximum)
```

**Rule:** `0 ≤ current_hp ≤ maximum_hp`

---

### 2. Ability Scores

```
✅ Valid:
- STR: 16  (within normal range)
- DEX: 8   (low but valid)
- CON: 20  (maximum for most characters)

❌ Invalid:
- STR: 22  (exceeds limit without magic items at low levels)
- DEX: 7   (below minimum)
- CON: 0   (would be dead)
```

**Rule:**
- Standard characters: `8 ≤ ability_score ≤ 20` (levels 1-19)
- With magic items/boons: up to 30
- Minimum to survive: 1 (3 or less means severe disability)

---

### 3. Hit Dice

```
✅ Valid:
- Available: 2 / 2  (full hit dice)
- Available: 0 / 2  (all used)

❌ Invalid:
- Available: 3 / 2  (more than total)
- Available: -1 / 2 (negative)
```

**Rule:** `0 ≤ hit_dice_used ≤ hit_dice_total`

---

### 4. Currency

```
✅ Valid:
- GP: 100  (positive)
- GP: 0    (broke but valid)

❌ Invalid:
- GP: -50  (can't have negative money)
```

**Rule:** All currency values must be ≥ 0

---

### 5. Proficiency Bonus

```
Level 1-4:  +2
Level 5-8:  +3
Level 9-12: +4
Level 13-16: +5
Level 17-20: +6
```

**Rule:** Proficiency bonus must match character level

---

### 6. Level-Appropriate Features

**Level 1 Fighter must have:**
- Fighting Style (one choice)
- Second Wind

**Level 2 Fighter must have:**
- Fighting Style
- Second Wind
- Action Surge

**Level 3 Fighter must have:**
- All of the above
- Martial Archetype chosen

**Rule:** Character must have all class features for their level

---

### 7. Armor Class Calculation

```
Base AC = 10 + DEX modifier + armor bonus + shield bonus + other bonuses
```

**Examples:**
```
✅ Valid:
- No armor, DEX +2: AC = 12
- Leather armor (AC 11 + DEX), DEX +3: AC = 14
- Chain mail (AC 16): AC = 16 (DEX doesn't apply)
- Chain mail + shield: AC = 18

❌ Invalid:
- Heavy armor + full DEX bonus (heavy armor limits DEX)
- AC = 25 with no magic items at level 1 (unrealistic)
```

---

### 8. Spell Slots (If Spellcaster)

```
✅ Valid:
- 1st Level: 0 / 2  (both used)
- 2nd Level: 1 / 3  (1 remaining)

❌ Invalid:
- 1st Level: 3 / 2  (used more than available)
- 1st Level: -1 / 2 (negative)
```

**Rule:** `0 ≤ spell_slots_used ≤ spell_slots_total`

---

### 9. Equipment Weight (If Tracking Encumbrance)

```
Carrying Capacity = STR score × 15 lbs

✅ Valid:
- STR 16: Can carry up to 240 lbs
- Equipment weighs 150 lbs: OK

❌ Invalid:
- STR 10: Can carry 150 lbs
- Equipment weighs 200 lbs: Over encumbered!
```

**Rule:** `equipment_weight ≤ STR × 15`

---

### 10. Skills and Proficiencies

```
✅ Valid:
- Athletics (STR +3, proficient +2): +5 total
- Acrobatics (DEX +2, not proficient): +2 total

❌ Invalid:
- Athletics (STR +3, proficient +2): +8 total (wrong math)
- 10 skill proficiencies at level 1 (classes give 2-4 + background)
```

**Rule:**
- Skill modifier = ability_modifier + (proficiency_bonus if proficient)
- Number of skill proficiencies must match class + background

---

## Validation Workflow

When `validate_character` is called:

1. **Read character file**
2. **Check required fields** - Are all mandatory fields present?
3. **Validate ranges** - Are all values within acceptable ranges?
4. **Check calculations** - Are modifiers calculated correctly?
5. **Verify D&D rules** - Does character follow 5e rules?
6. **Return detailed errors** - List all issues found

## Example Validation Output

### Valid Character:
```json
{
  "valid": true,
  "character_name": "Thork Ironforge",
  "level": 1,
  "class": "Fighter",
  "message": "Character is ready for adventure!"
}
```

### Invalid Character:
```json
{
  "valid": false,
  "errors": [
    "HP cannot be negative (current: -5)",
    "Ability score STR is 22 (max is 20 at level 1)",
    "Missing required field: Character class"
  ],
  "warnings": [
    "AC seems low for a Fighter (current: 10, expected 14+)",
    "No equipment listed - character may need gear"
  ]
}
```

---

## Common Validation Failures

### 1. Missing Required Fields
```
Error: "Missing required field: Character class"
Fix: Add class to basic information section
```

### 2. Invalid HP
```
Error: "HP cannot be negative (current: -5)"
Fix: Set HP to 0 (character is unconscious)
```

### 3. Ability Score Out of Range
```
Error: "Ability score STR is 25 (max is 20 at level 1)"
Fix: Reduce STR to 20 or less
```

### 4. Wrong Proficiency Bonus
```
Error: "Proficiency bonus should be +2 at level 1 (current: +3)"
Fix: Update proficiency bonus to +2
```

### 5. Missing Class Features
```
Error: "Level 1 Fighter must have Fighting Style"
Fix: Add Fighting Style to features section
```

---

## Validation Best Practices

1. **Validate after creation** - Always run validation after creating a new character
2. **Validate after level up** - Ensure all new features are added correctly
3. **Validate after major changes** - Check after big equipment or stat changes
4. **Read error messages carefully** - Validation output tells you exactly what's wrong
5. **Fix one error at a time** - Address errors in order, then re-validate

---

## When to Skip Validation

Validation can be skipped for:
- **Temporary characters** - NPCs that don't need full stats
- **Work in progress** - Character still being created
- **Homebrew rules** - Campaign uses modified rules

However, for player characters in active play, **always validate** before starting adventure!

---

## Validation Command

```
validate_character(session_name="session1", character_name="thork")
```

Returns detailed validation report with:
- ✅ Valid/Invalid status
- 🚨 Errors that must be fixed
- ⚠️  Warnings about potential issues
- 💡 Suggestions for improvement
