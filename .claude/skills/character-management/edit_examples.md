# Character Edit Examples

This guide shows safe patterns for editing character files using the Edit tool.

## General Principles

1. **Always Read first** - Use Read tool to get current character state
2. **Edit specific sections** - Don't rewrite entire file, just the section that changed
3. **Validate after editing** - Check against validation_rules.md for errors
4. **Use exact string matching** - old_string must match exactly (including spacing/formatting)

---

## Example 1: Taking Damage

**Scenario:** Thork takes 5 damage in combat

**Step 1: Read the character**
```
Read file_path="campaigns/a_most_potent_brew_party1/characters/thork.md"
```

**Step 2: Identify the section to edit**
```markdown
| **Hit Points** | 12 / 12 | Hit Die: d10 |
```

**Step 3: Use Edit tool**
```
old_string: "| **Hit Points** | 12 / 12 | Hit Die: d10 |"
new_string: "| **Hit Points** | 7 / 12 | Hit Die: d10 |"
```

**Step 4: Verify**
Read the character file to verify the change was applied correctly.

---

## Example 2: Healing

**Scenario:** Thork uses Second Wind to heal 1d10+1 = 8 HP

**Current state:**
```markdown
| **Hit Points** | 7 / 12 | Hit Die: d10 |
```

**After healing (7 + 8 = 15, but max is 12):**
```
old_string: "| **Hit Points** | 7 / 12 | Hit Die: d10 |"
new_string: "| **Hit Points** | 12 / 12 | Hit Die: d10 |"
```

**Note:** HP cannot exceed maximum. Cap at 12 HP.

---

## Example 3: Level Up

**Scenario:** Thork reaches level 2

**Multiple sections need updates:**

### Update 1: Basic Info
```
old_string: "| **Class & Level** | Fighter 1 |"
new_string: "| **Class & Level** | Fighter 2 |"
```

### Update 2: Experience
```
old_string: "| **Experience Points** | 300 / 300 |"
new_string: "| **Experience Points** | 300 / 900 |"
```

### Update 3: Hit Points (rolled 7 on d10, +2 CON mod = 9 HP gained)
```
old_string: "| **Hit Points** | 12 / 12 | Hit Die: d10 |"
new_string: "| **Hit Points** | 21 / 21 | Hit Die: d10 |"
```

### Update 4: Hit Dice
```
old_string: "| **Hit Dice** | 1 / 1 | 1d10 |"
new_string: "| **Hit Dice** | 2 / 2 | 2d10 |"
```

### Update 5: Add Class Feature (Action Surge)
Add to Features & Traits section:
```
old_string: "- **Second Wind:** As a bonus action, regain 1d10+1 hit points once per short or long rest"
new_string: "- **Second Wind:** As a bonus action, regain 1d10+2 hit points once per short or long rest\n- **Action Surge:** Once per short or long rest, take one additional action on your turn"
```

**Then verify:**
Read the character file to verify all changes were applied correctly.

---

## Example 4: Adding Equipment

**Scenario:** Thork finds a +1 longsword

### Update Weapons Table
```
old_string: "| Longsword | +5 | 1d8+3 | Slashing | Melee | Versatile (1d10) |"
new_string: "| Longsword +1 | +6 | 1d8+4 | Slashing | Melee | Versatile (1d10+1), magical |"
```

### Update Equipment List
```
old_string: "- Longsword"
new_string: "- Longsword +1 (magical)"
```

---

## Example 5: Spending Currency

**Scenario:** Thork buys healing potions for 50 GP

**Current currency:**
```markdown
- **Gold Pieces (GP):** 10
```

**After purchase (10 - 50 = -40, NOT ALLOWED):**
```
ERROR: Cannot afford this purchase. Thork only has 10 GP.
```

**Correct approach:** Check GP first before attempting purchase.

---

## Example 6: Short Rest

**Scenario:** Party takes short rest, Thork spends 1 Hit Die

### Update Hit Dice
```
old_string: "| **Hit Dice** | 2 / 2 | 2d10 |"
new_string: "| **Hit Dice** | 1 / 2 | 2d10 |"
```

### Update HP (rolled 6 on d10, +2 CON = 8 HP healed)
```
old_string: "| **Hit Points** | 13 / 21 | Hit Die: d10 |"
new_string: "| **Hit Points** | 21 / 21 | Hit Die: d10 |"
```

### Reset Short Rest Abilities
```
old_string: "- **Second Wind:** As a bonus action, regain 1d10+2 hit points once per short or long rest"
new_string: "- **Second Wind:** As a bonus action, regain 1d10+2 hit points once per short or long rest [AVAILABLE]"
```

---

## Example 7: Long Rest

**Scenario:** Party completes long rest

### Restore HP to Maximum
```
old_string: "| **Hit Points** | 8 / 21 | Hit Die: d10 |"
new_string: "| **Hit Points** | 21 / 21 | Hit Die: d10 |"
```

### Restore Hit Dice (regain half, minimum 1)
```
old_string: "| **Hit Dice** | 0 / 2 | 2d10 |"
new_string: "| **Hit Dice** | 1 / 2 | 2d10 |"
```

### Reset All Abilities
Mark all "once per long rest" and "once per short rest" abilities as available.

---

## Example 8: Updating Notes

**Scenario:** Add campaign note after session

```
old_string: "### Campaign Notes\n- Met the party at the Wizard's Tower Brewing Co.\n- Accepted job to clear rats from the brewery cellar"
new_string: "### Campaign Notes\n- Met the party at the Wizard's Tower Brewing Co.\n- Accepted job to clear rats from the brewery cellar\n- Explored ancient wizard ruins beneath brewery\n- Defeated giant rats and secured the cellar\n- Found potion of healing in the ruins"
```

---

## Common Mistakes to Avoid

### ❌ DON'T: Edit too much at once
```
old_string: [entire character file]
new_string: [entire character file with one change]
```

### ✅ DO: Edit specific sections
```
old_string: "| **Hit Points** | 12 / 12 | Hit Die: d10 |"
new_string: "| **Hit Points** | 7 / 12 | Hit Die: d10 |"
```

---

### ❌ DON'T: Forget to verify
```
Edit → Done
```

### ✅ DO: Always verify after edits
```
Edit → Read character → Check changes applied correctly
```

---

### ❌ DON'T: Allow invalid values
```
HP: -5 / 12  (HP can't be negative)
STR: 22      (Ability scores max at 20 for level 1-19)
GP: -10      (Can't have negative currency)
```

### ✅ DO: Enforce D&D rules
```
HP: 0 / 12   (Minimum HP is 0, character is unconscious)
STR: 20      (Respect ability score limits)
GP: 0        (Minimum currency is 0)
```

---

## Verification Checklist

After every edit, check:
- [ ] HP is between 0 and maximum
- [ ] Ability scores are valid (8-20 for most characters)
- [ ] Currency values are non-negative
- [ ] Hit dice used ≤ hit dice total
- [ ] Spell slots used ≤ spell slots total
- [ ] Equipment changes make sense (can't use items not owned)
- [ ] Level-appropriate features and abilities

Reference [validation_rules.md](validation_rules.md) for complete D&D 5e rules!
