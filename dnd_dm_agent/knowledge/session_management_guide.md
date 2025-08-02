# DM Agent Session Management Guide

> Complete guide for managing D&D game sessions and character sheets

---

## 🎯 DM Agent Core Role & Guidelines

### Primary Responsibilities
1. **Create immersive and engaging narratives**
2. **Manage game mechanics fairly and consistently**
3. **Respond to player actions creatively**
4. **Maintain game balance and fun for all players**
5. **Use dice rolls for appropriate situations**
6. **Track game state and character information**

### DM Style Guidelines
- Be descriptive and atmospheric in your narration
- Ask players what they want to do when appropriate
- Use the roll_dice tool for checks, attacks, and random events
- Use the manage_game_state tool to track locations and scenes
- Be encouraging but maintain challenge
- Follow D&D 5e rules when applicable
- Start each new conversation by setting an exciting scene and asking what the players want to do

---

## 📁 Directory Structure

When a game session is created, the following structure is automatically generated:

```
dnd_dm_agent/
└── game_sessions/
    └── [session_name]/
        ├── session_metadata.json
        ├── session_log.md
        └── characters/
            ├── [character_1].json
            ├── [character_1].md    ← Generated for human reading
            ├── [character_2].json
            ├── [character_2].md
            └── [character_n].json
```

---

## 🎮 Session Management Workflow

### 1. Starting a New Game Session

**Always create a session first** before any character creation:

```
DM Agent: "Welcome! Let's start your D&D adventure. What would you like to name this campaign?"
Player: "The Lost Mines of Phandelver"
DM Agent: Uses manage_game_session(action="create", session_name="The Lost Mines of Phandelver", dm_name="DM")
```

### 2. Character Creation Process

**Step-by-step character creation workflow:**

```
1. Get character name
2. Ask for class (use get_dnd_class_details for detailed info)
3. Ask for race/species  
4. Ask for background
5. Ask for alignment
6. Use tool_create_character(...) to create the character
7. Use guide_character_creation for step-by-step assistance
8. ALWAYS validate with tool_validate_character_readiness before gameplay
```

**Example:**
```
DM Agent: "Great! Now let's create your character. What's your character's name?"
Player: "Thorin Ironbeard"
DM Agent: "What class would you like to play? I can provide details about any class."
Player: "Tell me about Fighters"
DM Agent: Uses get_dnd_class_details("Fighter")
Player: "Fighter sounds good!"
DM Agent: Uses tool_create_character(session_name="The Lost Mines", 
                                    character_name="Thorin Ironbeard", 
                                    character_class="Fighter", race="Dwarf")
```

### 3. Character Validation & Readiness

**CRITICAL:** Always validate character readiness before starting gameplay:

```
DM Agent: Uses tool_validate_character_readiness(session_name, character_name)

If character is not ready:
- Use guide_character_creation to help fill missing information
- Required minimum fields: Name, Class & Level, Race, Background, Ability Scores, Hit Points, Armor Class
- Don't start adventures until all player characters are validated as ready
```

---

## 🔧 Character Sheet Management

### Primary Character Tools

Use the individual character management functions for all character operations:

- **tool_create_character()** - Create new characters with explicit parameters
- **tool_get_character()** - Retrieve existing character data  
- **tool_update_character()** - Update character fields using dictionary structure
- **tool_add_character_note()** - Add simple timestamped notes organized by session

---

## 🧠 Knowledge Access & Rules

### Knowledge Base Organization

The knowledge base is organized in folders for efficient searching:

```
knowledge/
├── player_handbook/
│   ├── spells/
│   │   ├── level_0_cantrips.md
│   │   ├── level_1_spells.md
│   │   └── ...
│   └── classes/
├── monster_manual/
│   ├── low_cr_monsters.md
│   ├── dragons.md
│   └── ...
├── classes_5e.md
├── session_management_guide.md
└── character_sheet_template.md
```

### Specialized Knowledge Tools

#### `get_spell_details(spell_name)`
- **Purpose**: Get detailed spell information from spell files only
- **Coverage**: Searches all spell files (cantrips, level 1+)
- **Examples**: 
  - `get_spell_details("Fire Bolt")` - finds cantrip details
  - `get_spell_details("Magic Missile")` - finds 1st level spell
  - `get_spell_details("Cure Wounds")` - finds healing spell
- **Returns**: `{"status": "success", "spell_name": "Fire Bolt", "information": [sections]}`

#### `get_monster_details(monster_name)`
- **Purpose**: Get detailed monster information from monster files only
- **Coverage**: Searches all monster files (low CR, dragons, etc.)
- **Examples**:
  - `get_monster_details("Goblin")` - finds basic monster stats
  - `get_monster_details("Red Dragon")` - finds dragon variants
  - `get_monster_details("Owlbear")` - finds specific creatures
- **Returns**: `{"status": "success", "monster_name": "Goblin", "information": [sections]}`

#### `get_dnd_class_details(class_name)`
- **Purpose**: Get comprehensive class information and features
- **Coverage**: Searches classes_5e.md file only
- **Examples**: `get_dnd_class_details("Wizard")`, `get_dnd_class_details("Rogue")`
- **Returns**: `{"status": "success", "class_name": "Wizard", "information": [sections]}`

### General Search Tool

#### `lookup_knowledge(query, specific_files=None)`
- **Purpose**: Search across ALL knowledge files when category is unclear
- **Regex Support**: Supports regex patterns for advanced searches
- **Case Insensitive**: Automatically handles case variations
- **Examples**:
  - `lookup_knowledge("advantage")` - general rule search
  - `lookup_knowledge("1d[0-9]+")` - find all dice notation patterns
  - `lookup_knowledge("fire.*damage")` - regex pattern for fire damage
  - `lookup_knowledge("Fighter", ["classes_5e"])` - search specific files
- **Returns**: `{"status": "success", "query": "...", "results": [{"file": "...", "sections": [...]}]}`

### Advanced Search Patterns

**Common Regex Patterns for DMs:**
- `"1d[0-9]+"` - Find dice notation (1d6, 1d10, etc.)
- `".*fire.*"` - Find anything fire-related
- `"CR [0-9]+"` - Find creatures by Challenge Rating
- `"[0-9]+-level"` - Find spells by level
- `"(advantage|disadvantage)"` - Find advantage/disadvantage rules

**Effective Search Tips:**
- Use specific functions first: `get_spell_details("Fireball")` vs `lookup_knowledge("Fireball")`
- Use regex for patterns: damage types, spell levels, CR ranges
- Try different term variations: "Fire Bolt" vs "fire bolt" vs "firebolt"
- Search specific files when you know the category

### Administrative Tools

#### `get_dm_guidance(topic=None)`
- Access session management tips and best practices
- Examples: `get_dm_guidance("combat")`, `get_dm_guidance()` for full guide

#### `list_available_knowledge()`
- See what knowledge files are available in the system

### Campaign Tools

#### `list_campaigns()`
- **Purpose**: Show all available pre-made campaign skeletons
- **Returns**: List of campaign names with their basic info
- **Use when**: Player asks "what adventures are available?" or you want to suggest structured campaigns

#### `load_campaign(campaign_name)`
- **Purpose**: Load a complete campaign skeleton for structured gameplay
- **Returns**: Full campaign content including story beats, NPCs, locations, encounters
- **Use when**: Starting a structured adventure or need campaign reference during play

#### Campaign Usage Workflow
```
1. Player wants structured adventure → use list_campaigns() to show options
2. Player chooses campaign → use load_campaign("campaign_name") 
3. Parse the skeleton content to understand:
   - Act/Beat structure and story progression
   - Level targets and completion triggers
   - NPC details and personality notes
   - Location descriptions and atmospheric details
   - Encounter suggestions and tactics
   - Agent guidance for adaptive pacing
4. Use skeleton as reference throughout session for:
   - Consistent NPC portrayal
   - Rich environmental descriptions
   - Story beat progression
   - Adaptive difficulty based on party level
```

#### Campaign Skeleton Structure
Campaign skeletons contain:
- **Acts & Beats**: Main story structure with accomplishments and branching
- **NPCs**: Detailed character profiles with speech patterns and motivations
- **Locations**: Atmospheric descriptions with sensory details
- **Encounters**: Creature descriptions with tactics and story purpose
- **Agent Guidance**: Instructions for handling player choices and pacing
- **Branching Outcomes**: Multiple resolution paths based on success level

**Example Usage:**
```
Agent: Let me check what campaigns we have available
[uses list_campaigns()]
Agent: "I have 'A Most Potent Brew' available - a brewery adventure for levels 1-2. Would you like to try it?"
Player: "Yes!"
[uses load_campaign("a_most_potent_brew")]
Agent: [Now has full skeleton with Glowkindle the brewery owner, the cellar with giant rats, ancient wizard ruins, etc.]
```

---

## 🎲 During Gameplay

### Game State Management
```
DM Agent: Uses manage_game_state(session_name, action, location, scene) for current location/scene tracking
DM Agent: ALWAYS follows up with update_session_log() to log location/scene changes
DM Agent: Uses roll_dice() for ability checks, attacks, and random events
DM Agent: Uses update_session_log() to record important moments
```

### Location & Scene Change Workflow
**CRITICAL:** Always log state changes immediately after updating them:
```
1. Use manage_game_state(session_name, "update_location", "Goblin Cave")
2. IMMEDIATELY use update_session_log(session_name, "The party enters the dark, musty Goblin Cave")
3. Use manage_game_state(session_name, "update_scene", "Torchlight flickers on damp stone walls...")
4. IMMEDIATELY use update_session_log(session_name, "Scene: The cave entrance is narrow with echoing sounds from within")
```

### Character Progression Tracking
- **Always update character sheets** when:
  - Damage is taken or healed
  - Equipment changes (gained/lost items)
  - Level ups occur
  - Abilities change or improve
  - XP is gained

### Event Logging
```python
update_session_log("The Lost Mines", "Thorin discovered a secret passage with Investigation 18")
update_session_log("The Lost Mines", "Party defeated goblin ambush, gained 50 XP each")
update_session_log("The Lost Mines", "Elara reached Wizard level 2")
```

---

## 📊 Session Metadata Structure

```json
{
  "session_name": "The Lost Mines of Phandelver",
  "dm_name": "Alice",
  "created_date": "2025-01-27T15:30:00",
  "last_played": "2025-01-27T18:45:00",
  "characters": ["Thorin Ironbeard", "Elara Moonwhisper"],
  "session_notes": "",
  "current_location": "Goblin Cave Entrance",
  "current_scene": "The party stands before a dark cave...",
  "history": [
    {
      "timestamp": "2025-01-27T18:30:00",
      "type": "location_change",
      "from": "Starting Location",
      "to": "Goblin Cave Entrance"
    },
    {
      "timestamp": "2025-01-27T18:35:00", 
      "type": "scene_change",
      "scene": "The party stands before a dark cave entrance, torchlight flickering against ancient stone..."
    }
  ]
}
```

---

## 📝 Session Log Example

```markdown
# The Lost Mines of Phandelver - Session Log

**DM:** Alice
**Created:** 2025-01-27 15:30

## Session History

### Session 1
*2025-01-27*

- Game session created
- Character 'Thorin Ironbeard' created (Fighter)
- Character 'Elara Moonwhisper' created (Wizard)
- Both characters validated and ready for gameplay
- [18:00] Party arrived at Goblin Cave
- [18:15] Thorin rolled Investigation: 18 (found secret passage)
- [18:20] Updated Thorin's character sheet: gained 25 XP
- [18:30] Combat with goblin guards
- [18:32] Thorin took 8 damage (HP: 17/25)
- [18:45] Party rested at cave entrance, Thorin healed 4 HP
```

---

## 🛠️ Complete Tool Reference

### Session Management
- `manage_game_session(action, session_name, dm_name)` - Create/list sessions
- `manage_game_state(session_name, action, location, scene)` - Track current state and sync to session metadata
- `update_session_log(session_name, event_description)` - Record events, including location/scene changes, checks, dice rolls

### Character Management  
- `tool_create_character(session_name, character_name, character_class, race, ...)` - Create new character
- `tool_get_character(session_name, character_name)` - Get existing character
- `tool_update_character(session_name, character_name, updates)` - Update character fields
- `tool_add_character_note(session_name, character_name, note)` - Add timestamped notes organized by session, a note should be added whenever there's a change in character sheet information and state the context and why.


### Character Creation & Validation
- `tool_validate_character_readiness(session_name, character_name)` - Check if ready to play
- `guide_character_creation(step, character_class, ability_method)` - Step-by-step guidance

### Knowledge & Rules
- `lookup_knowledge(query, specific_files)` - Search knowledge base
- `get_dnd_class_details(class_name)` - Get class information
- `get_dm_guidance(topic)` - Get DM best practices
- `list_available_knowledge()` - See available knowledge

### Game Mechanics
- `roll_dice(notation)` - Roll dice (e.g., "1d20+5", "2d6")

---

## 🎯 Best Practices Summary

### Session Flow
1. **Create session first** before any character creation
2. **Guide players through character creation** step by step using tools
3. **Always validate character readiness** before starting gameplay
4. **Check previous session logs** when resuming to ensure continuity
5. **Use knowledge tools** to provide accurate D&D information
6. **Update character data immediately** when changes occur
7. **Log location/scene changes immediately** after using manage_game_state
8. **Log important events** for session continuity

### Session Continuity
**When starting a conversation:**
1. Check recent session logs with previous events
2. Use manage_game_state(session_name, "get_state") to get current location, scene, and history
3. Review the history array to understand recent location/scene changes
4. Acknowledge recent character actions or story developments
5. Set scene based on where the story left off

### History Tracking
**Automatic history entries are created when:**
- Location changes: Records "from" and "to" locations with timestamp
- Scene changes: Records new scene description with timestamp
- All entries include ISO timestamps for chronological tracking

**Use history for:**
- Understanding session progression
- Referencing recent location changes
- Maintaining narrative continuity
- Tracking party movement through the adventure

### Character Management
TBF

### Knowledge Usage
1. **Reference knowledge base** instead of relying on training data
2. **Look up class details** when players ask about abilities
3. **Search for rules** when uncertain about mechanics
4. **Get DM guidance** for handling difficult situations

This system provides persistent memory, organized character tracking, and comprehensive D&D knowledge for engaging, well-managed campaigns!