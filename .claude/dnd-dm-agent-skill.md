# DnD DM Agent - Claude Code Skill

This skill provides repo-specific context for working with the DnD DM Agent codebase.

## Refactor Status

**Current State**: Migrating from Google ADK → Claude Agent SDK
- **Phase**: 3/6 complete (custom tools migrated, testing in progress)
- **Branch**: `refactor`
- **Plan**: See `refactor-plan.md` for detailed checklist

### What's Changed
- ✅ Removed Google ADK + LiteLLM dependencies
- ✅ Added Anthropic SDK (claude-agent-sdk)
- ✅ Migrated 5 core tools to SDK MCP format
- ⏸️ Removed 15 tools (replaced by built-in file tools)
- 🚧 Test cleanup in progress

### Architecture: Old vs New
```
OLD: Google ADK
- 20 tools (all custom)
- config/llm_engine.py wrapper
- LiteLLM for multi-provider support

NEW: Claude Agent SDK
- 5 custom tools (domain logic only)
- SDK MCP server pattern
- Direct Anthropic API
- Built-in file tools replace knowledge/session/campaign tools
```

## Known Issues & Workarounds

### Claude Agent SDK + MCP Servers Bug ⚠️
**Symptoms**: `CLIConnectionError: ProcessTransport is not ready for writing`

**Root Cause**: SDK bugs [#266](https://github.com/anthropics/claude-agent-sdk-python/issues/266) and [#386](https://github.com/anthropics/claude-agent-sdk-python/issues/386)
- String prompts fail with SDK MCP servers
- Partial fix only works with async generators

**Workaround** (implemented in `claude_agent.py:134`):
```python
async def prompt_generator():
    yield {
        "type": "user",
        "message": {"role": "user", "content": prompt},
        "parent_tool_use_id": None,
        "session_id": str(uuid.uuid4()),
    }

async for message in query(prompt=prompt_generator(), options=options):
    # process messages...
```

**Status**: Upstream bug, not our code. Workaround is correct implementation.

## Testing Strategy

### Unit Tests: `tests/`
- Test tool logic directly
- Fast, no API calls
- Mock file operations
- Run: `uv run pytest tests/ --ignore=tests/integration/`

### Integration Tests: `tests/integration/`
- Test agent end-to-end with real API
- Requires `ANTHROPIC_API_KEY` env var
- Slower, costs tokens
- Run: `uv run pytest tests/integration/ -v`
- Auto-skip if no API key set

### Test Cleanup Status
Removed (old ADK tests):
- ✅ `test_llm_engine.py` - LLM engine removed
- ✅ `test_claude_agent.py` - Wrapper tests removed (not directly testable)
- ⏸️ `test_knowledge_tools.py` - TODO: remove
- ⏸️ `test_campaign_tools.py` - TODO: remove
- ⏸️ `test_session_tools.py` - TODO: remove
- ⏸️ `test_utility_tools.py` - TODO: clean up manage_game_state tests

Keeping:
- `test_character_tools.py` - Character tools still used
- `tests/integration/test_claude_agent.py` - New integration tests

## Tool Development Pattern

### Adding a New Custom Tool

1. **Write underlying function** in `dnd_dm_agent/tools/`:
```python
def my_tool_logic(param: str) -> Dict[str, Any]:
    # Domain logic here
    return {"status": "success", "data": result}
```

2. **Wrap as SDK tool** in `claude_agent.py`:
```python
@tool("my_tool", "Description of what it does", {"param": str})
async def my_tool(args: dict[str, Any]) -> dict[str, Any]:
    result = _my_tool_logic(args["param"])
    return {"content": [{"type": "text", "text": str(result)}]}
```

3. **Register in MCP server**:
```python
dnd_tools = create_sdk_mcp_server(
    name="dnd",
    version="1.0.0",
    tools=[..., my_tool],  # Add here
)
```

4. **Add to allowed tools**:
```python
allowed_tools=[
    ...,
    "mcp__dnd__my_tool",  # Format: mcp__<server_name>__<tool_name>
]
```

5. **Update system prompt** to document the tool

## Environment Setup

### Required Environment Variables
- `ANTHROPIC_API_KEY` - Required for agent runtime and integration tests
  - Get from: https://console.anthropic.com/
  - Set: `export ANTHROPIC_API_KEY="sk-ant-..."`

### Running the Agent
```bash
# CLI mode
uv run python -m dnd_dm_agent.claude_agent "Roll 2d6+3"

# Interactive Python
python
>>> import asyncio
>>> from dnd_dm_agent.claude_agent import run
>>> asyncio.run(run("Create a session called test_session"))
```

## Common Debugging Scenarios

### "ProcessTransport is not ready for writing"
- **Cause**: SDK MCP bug with string prompts
- **Fix**: Already implemented in claude_agent.py (async generator workaround)
- **Action**: This is expected behavior, code is correct

### "Expected message type 'user' or 'control', got 'undefined'"
- **Cause**: Incorrect async generator message format
- **Fix**: Use proper format (see Known Issues section)
- **Check**: `claude_agent.py:134` for correct implementation

### Integration tests skipped
- **Cause**: `ANTHROPIC_API_KEY` not set
- **Fix**: `export ANTHROPIC_API_KEY="your-key"`
- **Verify**: `echo $ANTHROPIC_API_KEY`

### Tool not found by agent
- **Cause**: Tool not in `allowed_tools` list or wrong format
- **Fix**: Check `allowed_tools` uses `mcp__dnd__tool_name` format
- **Debug**: Print `options.allowed_tools` to verify

### Import errors for old modules
- **Cause**: Test files still importing removed modules (google.adk, litellm, config.llm_engine)
- **Fix**: Remove the test file (see Test Cleanup Status)

## Code Patterns to Follow

### Tool Return Format
All SDK tools must return:
```python
{"content": [{"type": "text", "text": "result string"}]}
```

### Character Tool Pattern
Character tools return `None` on failure (legacy pattern):
```python
result = _tool_create_character(...)
if result is None:
    return {"content": [{"type": "text", "text": "Failed to create character"}]}
return {"content": [{"type": "text", "text": str(result)}]}
```

### System Prompt Updates
When adding tools, update `SYSTEM_PROMPT` in `claude_agent.py` to document:
- Tool name
- What it does
- When to use it

## Data Locations

### Game Sessions
- Path: `dnd_dm_agent/game_sessions/[session_name]/`
- Structure:
  - `metadata.json` - Session info
  - `session_log.md` - Timestamped events
  - `characters/[name].json` - Character data

### Knowledge Base
- Path: `dnd_dm_agent/knowledge/`
- Format: Markdown files with D&D 5e content
- Access: Agent uses built-in file tools (no custom tools needed)

### Campaigns
- Path: `campaigns/[name]/campaign_skeleton.md`
- Structure: Acts → Beats hierarchy
- Access: Agent reads directly (no custom tools)

## Next Steps in Refactor

According to `refactor-plan.md`:

1. **Phase 4**: Design campaign skill system (load into system prompt)
2. **Phase 5**: Complete test migration
   - Add tests for remaining tool wrappers
   - Remove old tool tests
   - Add more integration tests
3. **Phase 6**: Final cleanup
   - Remove `google-adk`, `litellm` from any remaining references
   - Remove `config/llm_engine.py`
   - Remove deprecated tool files
   - Update CLAUDE.md with new architecture

## Quick Reference Commands

```bash
# Run agent
uv run python -m dnd_dm_agent.claude_agent "your prompt"

# Run all tests (unit only)
uv run pytest tests/ --ignore=tests/integration/

# Run integration tests
uv run pytest tests/integration/ -v

# Run specific test
uv run pytest tests/test_utility_tools.py::test_roll_dice_basic -v

# Lint and format
ruff check .
ruff format .
```
