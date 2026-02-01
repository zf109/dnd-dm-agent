# Refactor Plan: Google ADK → Claude Agent SDK

## Goal
Migrate from `google-adk` + `litellm` to Anthropic's Claude Agent SDK for better agent capabilities and simpler dependencies.

## Design Decisions

### Simplified Architecture
- **Use built-in file tools** instead of custom knowledge/session lookup wrappers
- **Keep only essential custom tools** that have domain logic (dice rolling, character validation)
- **Campaign as loadable skill** - campaign content injected into system prompt, no campaign-specific code

### Tool Reduction: 20 → ~5 custom tools

**Keep (custom logic required):**
- `roll_dice` - dice notation parsing
- `tool_create_character` - D&D character schema initialization
- `tool_update_character` - deep merge with schema validation
- `tool_validate_character_readiness` - domain validation rules
- `create_game_session` - folder structure + metadata initialization

**Remove (replaced by built-in file tools):**
- All 6 knowledge tools → agent reads `knowledge/` directly
- `get_session_log`, `list_game_sessions` → agent reads `game_sessions/` directly
- `list_campaigns`, `load_campaign` → agent reads `campaigns/` directly
- `tool_get_character` → agent reads character JSON directly
- `tool_add_character_note` → use `tool_update_character`
- `add_character_to_session` → agent updates metadata JSON directly
- `update_session_log` → agent appends to session_log.md directly
- `manage_game_state` → agent updates metadata JSON directly

### Data Compatibility
Existing data in `campaigns/`, `game_sessions/*/characters/` remains unchanged. Only the access pattern changes.

---

## Checklist

### Phase 1: Audit Current Tools ✅
- [x] Document all tool signatures from `knowledge_tools.py`
- [x] Document all tool signatures from `utility_tools.py`
- [x] Document all tool signatures from `session_tools.py`
- [x] Document all tool signatures from `character_tools/character_tools.py`
- [x] Document all tool signatures from `campaign_tools.py`
- [x] Note any ADK-specific patterns that need migration

### Phase 2: Scaffold New Agent ✅
- [x] Update `pyproject.toml` with `anthropic` dependency
- [x] Create `dnd_dm_agent/claude_agent.py` with agent loop
- [x] Configure built-in file tools (deferred - knowledge will become skills)

### Phase 3: Migrate Custom Tools Only ✅
- [x] Migrate `roll_dice`
- [x] Migrate `tool_create_character`
- [x] Migrate `tool_update_character`
- [x] Migrate `tool_validate_character_readiness`
- [x] Migrate `create_game_session`

### Phase 4: Campaign Skill System
- [ ] Design campaign loading mechanism (inject into system prompt)
- [ ] Test with existing campaign (`test_campaign/`)
- [ ] Update system prompt to guide agent on file access patterns

### Phase 5: Update Tests (In Progress)
- [ ] Update test fixtures for new SDK patterns
- [ ] Verify custom tool tests pass
- [x] Add integration tests for agent loop (initial test added: `test_agent_dice_roll`)

### Phase 6: Clean Up
- [ ] Remove `google-adk` dependency
- [ ] Remove `litellm` dependency
- [ ] Remove old `config/llm_engine.py`
- [ ] Remove deprecated tool files
- [ ] Update CLAUDE.md with new commands
- [ ] Update README if applicable

---

## Tool Audit (20 tools total)

### Knowledge Tools (`knowledge_tools.py`) - 6 tools

| Tool Name | Parameters | Returns | Notes |
|-----------|------------|---------|-------|
| `lookup_knowledge` | `query: str`, `specific_files: Optional[List[str]]` | `Dict[str, Any]` | Searches all markdown files with regex |
| `get_dnd_class_details` | `class_name: str` | `Dict[str, Any]` | Searches classes_5e.md |
| `get_spell_details` | `spell_name: str` | `Dict[str, Any]` | Searches player_handbook/spells/*.md |
| `get_monster_details` | `monster_name: str` | `Dict[str, Any]` | Searches monster_manual/*.md |
| `get_dm_guidance` | `topic: Optional[str]` | `Dict[str, Any]` | Searches session_management_guide.md |
| `list_available_knowledge` | _(none)_ | `Dict[str, Any]` | Lists all knowledge files with descriptions |

### Utility Tools (`utility_tools.py`) - 2 tools

| Tool Name | Parameters | Returns | Notes |
|-----------|------------|---------|-------|
| `roll_dice` | `notation: str` | `Dict[str, Any]` | Parses "2d6+3" notation |
| `manage_game_state` | `session_name: str`, `action: str`, `location: Optional[str]`, `scene: Optional[str]` | `Dict[str, Any]` | Actions: get_state, update_location, update_scene |

### Session Tools (`session_tools.py`) - 5 tools

| Tool Name | Parameters | Returns | Notes |
|-----------|------------|---------|-------|
| `create_game_session` | `session_name: str`, `dm_name: str = "DM"` | `Dict[str, Any]` | Creates folder structure + metadata |
| `list_game_sessions` | _(none)_ | `Dict[str, Any]` | Lists all sessions with metadata |
| `add_character_to_session` | `session_name: str`, `character_name: str` | `Dict[str, Any]` | Links character to session metadata |
| `update_session_log` | `session_name: str`, `log_entry: str` | `Dict[str, Any]` | Appends timestamped entry to session_log.md |
| `get_session_log` | `session_name: str` | `Dict[str, Any]` | Reads session_log.md content |

### Character Tools (`character_tools/`) - 5 tools

| Tool Name | Parameters | Returns | Notes |
|-----------|------------|---------|-------|
| `tool_create_character` | `session_name`, `character_name`, + 12 optional attrs (class, race, abilities, etc.) | `Optional[Dict[str, Any]]` | Returns None on failure |
| `tool_get_character` | `session_name: str`, `character_name: str` | `Optional[Dict[str, Any]]` | Returns None if not found |
| `tool_update_character` | `session_name: str`, `character_name: str`, `updates: Dict[str, Any]` | `Optional[Dict[str, Any]]` | Deep-merges updates |
| `tool_add_character_note` | `session_name: str`, `character_name: str`, `note: str` | `Optional[Dict[str, Any]]` | Adds timestamped note |
| `tool_validate_character_readiness` | `session_name: str`, `character_name: str` | `Dict[str, Any]` | Validates min required fields |

### Campaign Tools (`campaign_tools.py`) - 2 tools

| Tool Name | Parameters | Returns | Notes |
|-----------|------------|---------|-------|
| `list_campaigns` | _(none)_ | `Dict[str, Any]` | Lists campaign folders with skeleton files |
| `load_campaign` | `campaign_name: str` | `Dict[str, Any]` | Reads campaign_skeleton.md content |

---

## ADK-Specific Patterns to Migrate

### 1. Agent Definition Pattern
```python
# Current (Google ADK)
from google.adk.agents import Agent

root_agent = Agent(
    name="dungeon_master",
    model=claude_engine.create_model(),  # via LiteLLM wrapper
    description="...",
    instruction="...",
    tools=tools,  # List of functions
)
```

### 2. Tool Registration
- ADK uses plain Python functions directly
- Functions must return `Dict[str, Any]`
- Docstrings are used for tool descriptions
- Type hints are used for parameter schemas

### 3. LLM Engine Pattern
```python
# Current (config/llm_engine.py)
from litellm import completion

class LLMEngine:
    def create_model(self):
        # Returns ADK-compatible model wrapper
```

### 4. Return Value Convention
- All tools return `{"status": "success|error", ...}` dict
- Character tools return `None` on failure (inconsistent - consider standardizing)

---

## Migration Notes

### Claude Agent SDK Equivalents
- `Agent` → `anthropic.Agent` or custom agent class
- `tools` list → Tool definitions with `@tool` decorator or schema
- `instruction` → System prompt
- LiteLLM → Direct Anthropic client

### Breaking Changes to Handle
- Remove `google.adk` imports
- Remove `litellm` dependency
- Remove `config/llm_engine.py`
- Update tool function signatures if needed for Claude SDK format
