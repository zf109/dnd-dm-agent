---
name: dnd-knowledge-store
description: D&D 5e reference library containing classes, spells, monsters, character templates, and DM guidance. Use when answering questions about D&D rules, mechanics, spells, monsters, or class features.
allowed-tools: Read, Grep, Glob
---

# D&D 5e Knowledge Store

This skill provides access to a comprehensive D&D 5th Edition reference library. All knowledge files are located in the `knowledge/` subdirectory within this skill.

## Available References

### Character Creation & Classes
- **`knowledge/classes_5e.md`** - Complete reference for all D&D 5e player classes including features, abilities, hit dice, and progression
- **`knowledge/character_sheet_template.md`** - Character sheet structure and required fields

### Spells
- **`knowledge/player_handbook/spells/level_0_cantrips.md`** - All cantrips (0-level spells)
- **`knowledge/player_handbook/spells/level_1_spells.md`** - 1st level spells

### Monsters & Combat
- **`knowledge/monster_manual/dragons.md`** - Dragon stat blocks and tactics
- **`knowledge/monster_manual/low_cr_monsters.md`** - Low challenge rating creatures for starting parties

### DM Guidance
- **`knowledge/session_management_guide.md`** - Session running best practices, character management, game flow, and DM responsibilities

## How to Search the Knowledge Base

### 1. Search Across All Knowledge
Use Grep to search for specific terms or patterns:
```
Grep pattern="Fireball" path=".claude/skills/dnd-knowledge-store/knowledge"
```

### 2. Find Specific Files
Use Glob to list files by pattern:
```
Glob pattern=".claude/skills/dnd-knowledge-store/knowledge/**/*.md"
Glob pattern=".claude/skills/dnd-knowledge-store/knowledge/monster_manual/*.md"
```

### 3. Read Complete Files
Use Read to view full content:
```
Read file_path=".claude/skills/dnd-knowledge-store/knowledge/classes_5e.md"
```

## When to Use This Skill

Invoke this skill when players or the DM ask about:
- **Class features** - "What abilities does a Paladin get at level 5?"
- **Spell descriptions** - "How does Magic Missile work?"
- **Monster stats** - "What's the AC and HP of a Young Red Dragon?"
- **Character creation** - "What's the hit die for a Wizard?"
- **DM guidance** - "How should I handle session management?"
- **Rules clarification** - "What ability modifier does a Monk use?"

## Best Practices

1. **Start with search** - Use Grep to find relevant sections before reading entire files
2. **Read selectively** - Only read full files when you need comprehensive information
3. **Cross-reference** - Information about classes may reference spells or abilities in other files
4. **Cite sources** - When answering player questions, mention which reference you used (e.g., "According to classes_5e.md...")

## Directory Structure

```
knowledge/
├── classes_5e.md                    # All player classes
├── character_sheet_template.md     # Character sheet structure
├── session_management_guide.md     # DM best practices
├── player_handbook/
│   └── spells/
│       ├── level_0_cantrips.md     # Cantrips
│       └── level_1_spells.md       # 1st level spells
└── monster_manual/
    ├── dragons.md                   # Dragon stat blocks
    └── low_cr_monsters.md           # Low CR creatures
```

Use this knowledge base to provide accurate, rules-compliant D&D 5e information to players and assist with game mastering.
