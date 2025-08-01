# Story Module Architecture Design

*Working document for iterating on story module system architecture*

## Design Approach

**Step 1**: Define optimal campaign structure for agent effectiveness
**Step 2**: Figure out how to convert messy input into that structure

## Agent-Optimal Campaign Structure

*What does the agent need to successfully run a campaign?*

### Core Agent Requirements

#### 1. **Current State Awareness**
The agent needs to know:
- Where players are in the story right now
- What just happened in the last session
- What NPCs are present and their current attitudes
- What locations are available and accessible
- What quests/conflicts are active
- What information players have discovered

#### 2. **Available Content Pool**
The agent needs access to:
- NPCs that can appear (with motivations, relationships, dialogue hooks)
- Locations that can be visited (with descriptions, encounters, secrets)
- Story beats that can happen (events, revelations, conflicts)
- Encounters appropriate for current party level
- Environmental details and atmosphere

#### 3. **Story Progression Logic**
The agent needs to understand:
- What are the major story milestones/beats
- How player actions trigger consequences
- When characters should level up
- How difficulty scales with party advancement
- What the ultimate resolution possibilities are

#### 4. **Continuity Tracking**
The agent needs to maintain:
- What has been established as "true" in this world
- Who knows what information
- What consequences are still playing out
- What promises/threats have been made
- What relationships have been formed

### Proposed Campaign Structure

Based on agent needs, here's an optimal campaign structure:

```
campaigns/[campaign_name]/
├── current_state.md          # Where we are right now
├── story_progression.md      # Major beats and how they connect
├── content_library/          # Available content to draw from
│   ├── npcs.md              # Characters with motivations
│   ├── locations.md         # Places with details and hooks
│   ├── encounters.md        # Combat and social challenges
│   ├── events.md            # Story beats and developments
│   └── secrets.md           # Hidden information and reveals
├── continuity/              # What's been established
│   ├── world_facts.md       # Established truths about the world
│   ├── relationships.md     # NPC attitudes and connections
│   ├── consequences.md      # Ongoing results of player actions
│   └── session_history.md   # What has happened
└── campaign_config.md       # Basic setup (levels, themes, etc.)
```

## Story Skeleton Structure

Based on the clarifications, here's the optimal nested structure for story progression:

### **Two-Level Nested Structure**

The campaign skeleton uses Acts containing Beats, with rich atmospheric details for immersive storytelling:

```markdown
# Campaign Story Skeleton Template

## Act 1: [Act Title] (Levels X-Y)
**Story Goal**: [Primary objective of this act]
**Level Target**: Characters should reach level Y by end of act
**Completion Triggers**: [What accomplishments complete this act]

### Beat 1.1: [Beat Title]
- **Accomplishment**: [What the party should achieve]
- **Agent Guidance**: [Adaptive instructions for pacing/difficulty]
- **Branching**: [Available paths/approaches]
- **Key Elements**: [Important story beats, NPCs, locations]
- **Atmospheric Details**: [Sensory descriptions for immersion]

### Beat 1.2: [Beat Title]
- **Accomplishment**: [What the party should achieve]
- **Agent Guidance**: [Adaptive instructions for pacing/difficulty] 
- **Branching**: [Available paths/approaches]
- **Key Elements**: [Important story beats, NPCs, locations]
- **Atmospheric Details**: [Sensory descriptions for immersion]

[Additional beats as needed...]
```

### **Enhanced Content Sections**

Each campaign skeleton includes detailed atmospheric descriptions:

```markdown
## Key NPCs
### [NPC Name] ([Role])
**Current Role**: [Function in story]
**Motivation**: [What drives them]
**Personality**: [Character traits]
**Physical Description**: [Appearance details]
**Speech Patterns**: [How they talk]
**Available Interactions**: [What party can do with them]
**Atmospheric Details**: [Sensory elements, mannerisms]

## Key Locations
### [Location Name]
**Description**: [Basic function]
**Visual Details**: [What it looks like]
**Sensory Elements**: [Sounds, smells, atmosphere]
**Features**: [Important elements]
**Story Function**: [Role in narrative]

## Encounters
### [Encounter Name]
**Physical Description**: [Appearance of creatures/challenges]
**Behavioral Details**: [How they act/react]
**Atmospheric Elements**: [Environmental storytelling]
**Tactics**: [How they fight/behave]
**Story Purpose**: [Why this encounter exists]
```

### **Example: "A Most Potent Brew" Campaign Skeleton**

To demonstrate the structure, we've created a complete example campaign based on a popular D&D 5e adventure:

**Campaign**: A Most Potent Brew (Single-session brewery adventure)
**Structure**: 1 Act with 4 Beats (Levels 1-2)
**File Location**: `campaigns/a_most_potent_brew/campaign_skeleton.md`

**Key Features Demonstrated**:
- **Rich Atmospheric Descriptions**: Each location includes visual details, sensory elements, and environmental storytelling
- **Detailed NPC Profiles**: Physical descriptions, speech patterns, and behavioral details
- **Encounter Atmosphere**: Creature descriptions with behavioral and tactical details
- **Treasure Descriptions**: Magic items with evocative descriptions and discovery context
- **Agent Guidance**: Adaptive instructions for handling different player approaches
- **Branching Outcomes**: Multiple resolution paths based on party success level

**Example NPC Structure**:
```markdown
### Glowkindle (Brewery Owner)
**Physical Description**: A stout halfling with flour-dusted apron and worried eyes. Her hands are permanently stained amber from years of brewing, and she gestures emphatically when explaining the rat problem.
**Speech Patterns**: "Listen here, adventurers..." "Big as dogs, I tell you!" "My livelihood depends on this!"
**Atmospheric Details**: Glowkindle's usually cheerful demeanor is clouded with worry. She wrings her hands constantly and keeps glancing toward the cellar stairs.
```

**Example Location Structure**:
```markdown
### The Brewery Cellars
**Visual Details**: Rough-hewn stone walls lined with oak barrels of various sizes. A jagged hole in the far wall reveals impenetrable darkness beyond.
**Sensory Elements**: Cool, damp air tinged with yeast and alcohol, echoing drips, scratching sounds from the shadows
**Story Function**: Entry point to adventure, evidence of rat problem
```

This example serves as a template for creating other campaign skeletons with the same level of atmospheric detail and structural guidance.

### **Adaptive Pacing System**

The agent balances story accomplishments with character levels:

```markdown
## Level-Accomplishment Balancing

### If Party Level > Expected Level for Beat:
- **Rush the accomplishment**: Have story events find the party
- **Escalate quickly**: Skip slow buildup, jump to action/revelation
- **Example**: Party is level 3 but hasn't uncovered corruption → Mayor gets attacked, evidence is obvious

### If Party Level < Expected Level for Beat: 
- **Add encounters**: More challenges before major story beat
- **Deepen exploration**: More investigation, side quests, character development
- **Example**: Party found corruption at level 2 → Add political complications, rivals, deeper mystery

### Branching Path Management:
- **Prerequisites clear**: Each act/beat shows what must be completed first
- **Multiple entry points**: Different paths can lead to same beats
- **Consequence tracking**: Earlier choices affect later content availability
```

### **Agent Decision Points**

Key guidance for the agent without micromanaging:

```markdown
## When to Escalate Tension
- Party seems disengaged → Bring conflict to them (raid, arrest, threat)
- Party is over-leveled → Rush to next major story beat
- Party is under-leveled → Add challenges that grant XP/advancement

## How to Handle Player Choices
- **Ignore main quest**: Have consequences find them (town suffers, threats grow)
- **Unexpected approach**: Use branching paths to accommodate, not block
- **Get stuck**: Provide new information through NPCs, events, or discoveries

## Content Selection Guidelines  
- **Combat encounters**: Match current party level + story context
- **NPC interactions**: Use personalities that fit current story beat
- **Information reveals**: Balance with what party has already discovered
```

### **Simplified Campaign Model**

Based on the clarification that **session = campaign**:

```markdown
## Campaign Session Structure
- **One campaign per session**: Complete story arc in single session
- **Flexible pacing**: Story can be 2 hours or 6 hours depending on party engagement
- **Self-contained**: Each campaign resolves, no multi-session continuity required
- **Reusable**: Same campaign skeleton can be run multiple times with different outcomes

## Story Skeleton Benefits
- **Adaptive**: Responds to party level and choices
- **Complete**: Full story arc from start to resolution  
- **Branching**: Multiple paths through same content
- **Scalable**: Works for short or long sessions
```

## Simplified Agent-Driven Architecture

### Campaign Creation Approach

**Philosophy**: Let the agent handle all parsing and structuring through natural language processing, not complex code.

#### Interactive Campaign Creation Process

1. **User initiates**: "I want to create a campaign"
2. **Agent gets instructions**: Loads campaign creation guide
3. **Agent asks questions**: Extracts info and fills gaps through conversation
4. **Agent writes skeleton**: Creates structured campaign using writing tools
5. **Agent adds content**: Optionally creates supporting content (NPCs, locations, etc.)

#### Tool-Based Implementation

**Campaign Creation Tools**:
- `get_campaign_creation_guide()` - Loads instructions for agent (like session management guide)
- `write_campaign_skeleton(campaign_name, skeleton_content)` - Core story structure
- `write_campaign_content(campaign_name, content_type, content)` - Flexible content writing
- `list_campaigns()` - View existing campaigns (future)
- `get_campaign_details(campaign_name)` - Load campaign info (future)

**Campaign Creation Guide** should instruct agent to:
1. Extract themes, conflicts, NPCs, locations from user input
2. Ask clarifying questions to ensure minimum viable skeleton
3. Create Act/Beat structure following design pattern
4. Use creative freedom for additional content

**Minimum Required Structure**: Story skeleton with Acts and Beats including:
- Level targets
- Accomplishment triggers
- Agent guidance notes
- Branching paths

### Simplified Campaign Storage Structure

```
campaigns/
├── [campaign_name]/
│   ├── campaign_skeleton.md        # Core story structure (REQUIRED)
│   ├── npcs.md                     # Character details (optional)
│   ├── locations.md                # World building (optional)
│   ├── encounters.md               # Combat/challenges (optional)
│   └── notes.md                    # Additional content (optional)
```

**Focus**: Start with just the skeleton. Agent can add other content as needed during creation or later.

### Campaign Usage During Play

**Runtime Integration**: Campaign skeleton provides guidance during sessions:
- Agent reads skeleton to understand story structure
- Uses Act/Beat progression to guide pacing
- Follows adaptive pacing rules (level vs accomplishment balancing)
- References supporting content (NPCs, locations) as needed

**Future Evolution**: Campaign content can be updated as play progresses, but focus initially on creation and basic usage.

## Example Workflow

### DM Input (Messy & Incomplete)
```
"I want to run something with:
- Pirates threatening coastal town
- Ancient dragon sleeping under the island  
- Party is level 3, 4 players
- Should take about 6-8 sessions
- Maybe some political intrigue?
- I have this cool NPC idea - a reformed pirate captain
- Also the town council might be corrupt?"
```

### Agent Processing Steps
1. **Content Analysis**:
   - "This sounds like a 3-act adventure with political and mythical elements"
   - "I can see themes of redemption (reformed pirate) and corruption (town council)"
   - "The dragon suggests an escalating power level from 3rd to 5th level"

2. **Gap Identification**:
   - "Need more details on the political intrigue mechanics"
   - "How does the dragon connect to the pirates?"
   - "What's the town's relationship to both threats?"

3. **Clarifying Questions**:
   - "Should the dragon be the final boss or a potential ally against the pirates?"
   - "Is the town council working with the pirates, or are these separate threats?"
   - "What's your reformed pirate captain's relationship to the current pirate crew?"

4. **Structure Suggestion**:
   - "I can organize this as: Investigation → Confrontation → Climax"
   - "Acts could be: Town Politics → Island Expedition → Final Convergence"

### Agent Output (Structured Campaign)
```markdown
# Crimson Tides Campaign

## Campaign Overview  
- **Level Range**: 3-5 (starting at 3rd, ending around 5th)
- **Duration**: 6-8 sessions  
- **Themes**: Political corruption, redemption, ancient power
- **Tone**: Nautical adventure with political intrigue

## Story Structure

### Act 1: Coastal Troubles (Sessions 1-2)
**Goal**: Establish threats and political landscape

- Pirates raiding merchant ships, town economy suffering
- Town council divided on response - some want military action, others negotiation
- Introduction of Captain Redbeard (reformed pirate NPC) - why did they leave piracy?
- PC investigation reveals council corruption - someone's feeding information to pirates
- **Hook for Act 2**: Pirates' base discovered on mysterious Dragon Isle

**Key NPCs**: 
- Captain Redbeard (Reformed pirate, potential ally/guide)
- Councilor Blackwater (Corrupt, secret pirate informant)
- Mayor Goodhaven (Honest but overwhelmed)

### Act 2: Island Mysteries (Sessions 3-5)  
**Goal**: Explore pirate stronghold and discover ancient secrets

- Journey to Dragon Isle with Redbeard's guidance
- Pirate base investigation - not just raiders, they're searching for something
- Discovery of ancient dragon lore - the "sleeping dragon" is real
- Political maneuvering: pirates trying to wake dragon for power
- **Cliffhanger**: Party actions accidentally begin dragon awakening process

**Key Locations**:
- Dragon Isle Pirate Fortress
- Ancient Dragon Temple (underground)
- Sleeping Dragon's Chamber

### Act 3: Awakening Thunder (Sessions 6-8)
**Goal**: Resolve all story threads in climactic confrontation

- Dragon begins to stir due to party/pirate activities
- Final confrontation with Pirate Lord Crimson Jack
- Political resolution - expose corruption, restore town leadership  
- Dragon encounter - combat, negotiation, or alliance?
- **Resolution**: Town saved, political corruption cleansed, dragon's fate decided

## Identified Gaps & Questions for DM

1. **Dragon's Motivation**: Why is it sleeping? What wakes it fully?
2. **Pirate Lord Details**: Who is Crimson Jack and why do they want the dragon?
3. **Corruption Mechanics**: How deep does town council corruption go?
4. **Redbeard's History**: What's their connection to current pirates?

## Suggested Next Steps

1. **Flesh out NPC motivations** - especially the three key figures
2. **Define dragon's nature** - ancient guardian, slumbering tyrant, or something else?
3. **Detail the corruption** - is it greed, coercion, or ideological?
4. **Plan session 1 opening** - how do PCs get involved?

---

*This structure can evolve based on player choices and DM preferences. The agent will adapt and refine as the campaign develops.*
```

## Simple Tool Architecture

### Core Campaign Tools
```python
# Campaign Creation (Priority)
def get_campaign_creation_guide()  # Load instructions like get_dm_guidance()
def write_campaign_skeleton(campaign_name, skeleton_content)  # Core structure
def write_campaign_content(campaign_name, content_type, content)  # Flexible content

# Campaign Management (Future)
def list_campaigns()  # View existing campaigns
def get_campaign_details(campaign_name)  # Load campaign for reference
def load_campaign_skeleton(campaign_name)  # Get story structure for session guidance
```

**Implementation Focus**: Start with creation tools only. Management tools can be added later.

### Integration with Existing Systems
- **Character Advancement**: Story milestones trigger level-ups automatically
- **Session Logging**: Enhanced to capture story developments, not just mechanics
- **Knowledge Base**: Campaign-specific NPCs, locations become searchable content
- **Combat System**: Encounters generated based on campaign context and pacing

## Key Benefits of This Architecture

### For Dungeon Masters
1. **Effortless Organization**: Drop messy ideas, receive structured campaigns
2. **Intelligent Collaboration**: Agent asks the right questions to fill gaps  
3. **Adaptive Structure**: Campaign evolves naturally with actual play
4. **Reduced Prep Time**: Agent handles consistency, pacing, and continuity

### For Players  
1. **Consistent World**: Agent maintains story logic and consequences
2. **Reactive Storytelling**: Campaign adapts to player choices and interests
3. **Rich Continuity**: Actions in session 1 matter in session 8

### For System Architecture
1. **Scalable**: Handles campaigns from simple to complex
2. **Flexible**: Works with any input quality or format
3. **Maintainable**: Clear separation between content and logic
4. **Extensible**: Easy to add new content types and generation methods

## Open Questions & Design Decisions

### Technical Considerations
1. **Content Parsing**: How sophisticated should PDF/document parsing be?
2. **Storage Format**: JSON metadata + Markdown content, or pure Markdown with YAML frontmatter?
3. **Version Control**: How do we track campaign evolution over time?
4. **Sharing**: Should campaigns be exportable/importable between systems?

### User Experience Design
1. **Onboarding Flow**: What's the ideal DM experience for first campaign creation?
2. **Iteration Process**: How does DM review and refine agent suggestions?
3. **Control Balance**: How much automation vs. DM control over story development?
4. **Error Recovery**: What happens when agent misunderstands DM intent?

### Integration Complexity
1. **Character Sheet Sync**: How tightly should campaign progression integrate with character advancement?
2. **Session Tool Overlap**: Which existing session tools need modification vs. replacement?
3. **Knowledge Base Growth**: Should campaign-specific content become part of searchable knowledge?
4. **Multi-Campaign Management**: How do we handle DMs running multiple campaigns?

---

## Implementation Status

### ✅ Completed
1. **Campaign skeleton format defined**: Two-level nested structure (Acts/Beats) with atmospheric details
2. **Example campaign created**: "A Most Potent Brew" demonstrates complete skeleton structure
3. **Storage structure established**: `campaigns/[campaign_name]/campaign_skeleton.md` format
4. **Atmospheric enhancement patterns**: Rich descriptions for NPCs, locations, encounters, and treasures

### 🔄 Next Steps for Implementation

1. **Create campaign creation guide**: Markdown file with instructions for agent
2. **Implement basic tools**: `get_campaign_creation_guide()` and `write_campaign_skeleton()`
3. **Add flexible content tool**: `write_campaign_content()` for NPCs, locations, etc.
4. **Test interactive creation**: Agent-driven campaign creation from user input
5. **Add management tools**: Campaign listing and loading (lower priority)

### 📋 Design Validation

The "A Most Potent Brew" example validates key design decisions:
- **Single-session scope**: Perfect for testing story module system
- **Rich atmospheric detail**: Enables immersive DM agent narration
- **Flexible structure**: Acts/Beats adapt to different story lengths
- **Agent guidance**: Clear instructions for adaptive pacing and player choice handling
- **Branching outcomes**: Multiple resolution paths maintain player agency

**Key Principle**: Agent handles all complexity through natural language and simple file I/O tools.

*This document should evolve as we prototype and test the concepts.*