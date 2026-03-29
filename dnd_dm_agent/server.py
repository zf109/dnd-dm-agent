"""FastAPI WebSocket server exposing the D&D DM Agent."""

import asyncio
import json
import re
import shutil
from pathlib import Path

from claude_agent_sdk import AssistantMessage, ClaudeSDKClient, TextBlock, ToolResultBlock, ToolUseBlock
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .claude_agent import get_options, process_message, run_bookkeeping_subagent
from .logging_config import bookkeeping_logger, dm_logger, logger

PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(title="D&D DM Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_instance_meta(instance_dir: Path) -> dict:
    """Parse campaign_progress.md to extract display metadata for an instance."""
    progress = instance_dir / "campaign_progress.md"
    name = instance_dir.name
    defaults = {"name": name, "display_name": name.replace("_", " ").title(), "character": "", "beat": ""}

    if not progress.exists():
        return defaults

    text = progress.read_text()

    # display_name: Template + Instance from header lines
    template_m = re.search(r"\*\*Template:\*\*\s*(\S+)", text)
    instance_m = re.search(r"\*\*Instance:\*\*\s*(\S+)", text)
    if template_m and instance_m:
        t = template_m.group(1).replace("_", " ").title()
        i = instance_m.group(1).replace("_", " ").title()
        display_name = f"{t} \u2014 {i}"
    else:
        display_name = name.replace("_", " ").title()

    # character: first Party list entry
    char_m = re.search(r"- \*\*(.+?)\*\*\s*\((.+?)\)", text)
    character = f"{char_m.group(1)} \u00b7 {char_m.group(2)}" if char_m else ""

    # beat: Act N + Beat text
    act_m = re.search(r"- \*\*Act:\*\*\s*Act\s*(\d+)", text)
    beat_m = re.search(r"- \*\*Beat:\*\*\s*(.+?)(?:\s*\([^)]*\))?$", text, re.MULTILINE)
    if beat_m:
        beat_text = beat_m.group(1).strip()
        beat = f"Act {act_m.group(1)} \u00b7 {beat_text}" if act_m else beat_text
    else:
        beat = ""

    return {"name": name, "display_name": display_name, "character": character, "beat": beat}


# =============================================================================
# REST Endpoints
# =============================================================================


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/campaigns")
async def list_campaigns():
    campaigns_dir = PROJECT_ROOT / "campaigns"
    if not campaigns_dir.exists():
        return {"instances": []}
    dirs = sorted(d for d in campaigns_dir.iterdir() if d.is_dir())
    return {"instances": [_parse_instance_meta(d) for d in dirs]}


@app.get("/api/templates")
async def list_templates():
    templates_dir = PROJECT_ROOT / "available_campaigns"
    if not templates_dir.exists():
        return {"templates": []}
    result = []
    for d in sorted(templates_dir.iterdir()):
        if not d.is_dir():
            continue
        pregen = d / "pregenerated_characters"
        characters = []
        if pregen.exists():
            characters = sorted(
                [{"name": f.stem, "display_name": f.stem.replace("_", " ").title()} for f in pregen.glob("*.md")],
                key=lambda c: c["name"],
            )
        result.append(
            {
                "name": d.name,
                "display_name": d.name.replace("_", " ").title(),
                "characters": characters,
            }
        )
    return {"templates": result}


class CreateCampaignRequest(BaseModel):
    template: str
    character: str


@app.post("/api/campaigns", status_code=201)
async def create_campaign(req: CreateCampaignRequest):
    from .tools.campaign_instance_tools import create_campaign_instance

    template_path = PROJECT_ROOT / "available_campaigns" / req.template
    if not template_path.exists():
        raise HTTPException(status_code=400, detail=f"Template '{req.template}' not found")

    result = create_campaign_instance(req.template, req.character)

    if result["status"] == "error":
        if "already exists" in result.get("error_message", ""):
            raise HTTPException(status_code=409, detail=result["error_message"])
        raise HTTPException(status_code=500, detail=result["error_message"])

    pregen_src = template_path / "pregenerated_characters" / f"{req.character}.md"
    if pregen_src.exists():
        instance_dir = PROJECT_ROOT / "campaigns" / f"{req.template}_{req.character}"
        dst = instance_dir / "characters" / f"{req.character}.md"
        dst.write_text(pregen_src.read_text())

    return {"instance": f"{req.template}_{req.character}", "character": req.character}


@app.delete("/api/campaigns/{campaign_instance}", status_code=204)
async def delete_campaign(campaign_instance: str):
    instance_path = PROJECT_ROOT / "campaigns" / campaign_instance
    if not instance_path.exists() or not instance_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Instance '{campaign_instance}' not found")
    shutil.rmtree(instance_path)


@app.get("/api/campaigns/{campaign_instance}/characters")
async def list_characters(campaign_instance: str):
    chars_dir = PROJECT_ROOT / "campaigns" / campaign_instance / "characters"
    if not chars_dir.exists():
        return {"characters": []}
    characters = [f.stem for f in chars_dir.glob("*.md")]
    return {"characters": sorted(characters)}


@app.get("/api/character/{campaign_instance}/{character_name}")
async def get_character(campaign_instance: str, character_name: str):
    path = PROJECT_ROOT / "campaigns" / campaign_instance / "characters" / f"{character_name}.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Character {character_name} not found")
    return {"markdown": path.read_text(), "name": character_name}


# =============================================================================
# WebSocket Endpoint
# =============================================================================


def _make_tool_display_name(tool_name: str, tool_input: dict) -> str:
    """Convert tool name + input into a context-aware display string."""

    def _stem(path: str) -> str:
        """Extract the filename stem from a path."""
        return path.rstrip("/").split("/")[-1].replace(".md", "").replace("_", " ")

    if tool_name == "mcp__dnd__roll_dice":
        notation = tool_input.get("notation", "dice")
        return f"Rolling {notation}"

    if tool_name == "mcp__dnd__create_campaign_instance":
        return "Creating campaign"

    if tool_name in ("Read", "Write", "Edit"):
        path = str(tool_input.get("file_path", ""))
        verb = {"Read": "Reading", "Write": "Creating", "Edit": "Updating"}[tool_name]
        if "/characters/" in path:
            char = _stem(path).replace(" md", "").title()
            action = {"Read": "Reading", "Write": "Creating", "Edit": "Updating"}[tool_name]
            return f"{action} {char}'s sheet"
        if "campaign_progress" in path:
            return f"{verb} campaign progress"
        if "campaign_log" in path:
            return "Logging session events" if tool_name == "Edit" else f"{verb} session log"
        if "campaign_guide" in path:
            return "Reading campaign guide"
        if "npcs" in path:
            return f"{verb} NPC notes"
        if "locations" in path:
            return f"{verb} locations"
        if "encounters" in path:
            return f"{verb} encounters"
        return f"{verb} files"

    if tool_name == "Glob":
        pattern = str(tool_input.get("pattern", ""))
        if "characters" in pattern:
            return "Finding characters"
        if "campaigns" in pattern or "available_campaigns" in pattern:
            return "Finding campaigns"
        if "skills" in pattern:
            return "Finding skills"
        return "Finding files"

    if tool_name == "Grep":
        return "Searching knowledge"

    if tool_name == "Skill":
        skill_map = {
            "campaign-guide": "Loading campaign guide",
            "character-management": "Managing character",
            "dnd-knowledge-store": "Consulting rulebook",
            "dnd-dm": "Consulting DM guide",
        }
        skill = str(tool_input.get("skill", ""))
        return skill_map.get(skill, "Consulting knowledge")

    return tool_name.lower().replace("_", " ")


def _make_tool_tooltip(tool_name: str, tool_input: dict) -> str:
    """Return a detailed tooltip string for a tool call."""
    if tool_name in ("Read", "Write", "Edit"):
        return str(tool_input.get("file_path", ""))
    if tool_name == "Glob":
        return str(tool_input.get("pattern", ""))
    if tool_name == "Grep":
        pattern = tool_input.get("pattern", "")
        path = tool_input.get("path", "")
        return f'"{pattern}" in {path}' if path else f'"{pattern}"'
    if tool_name == "Skill":
        skill = tool_input.get("skill", "")
        args = tool_input.get("args", "")
        return f"{skill}: {args}" if args else skill
    if tool_name == "mcp__dnd__roll_dice":
        return str(tool_input.get("notation", ""))
    if tool_name == "mcp__dnd__create_campaign_instance":
        return f"{tool_input.get('campaign_template', '')} / {tool_input.get('instance_name', '')}"
    return ""


async def _forward_bookkeeping_to_ws(
    websocket: WebSocket,
    user_msg: str,
    dm_response: str,
    campaign: str,
    character: str,
) -> None:
    """Forward bookkeeping subagent tool-use events to the WebSocket."""
    try:
        async for message in run_bookkeeping_subagent(user_msg, dm_response, campaign, character):
            if not isinstance(message, AssistantMessage):
                continue
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    try:
                        await websocket.send_json(
                            {
                                "type": "tool_use",
                                "tool_name": block.name,
                                "tool_input": block.input,
                                "display_name": _make_tool_display_name(block.name, block.input),
                                "tooltip": _make_tool_tooltip(block.name, block.input),
                                "source": "bookkeeping",
                            }
                        )
                    except Exception:
                        pass  # WebSocket may have closed
    except Exception as e:
        bookkeeping_logger.error(f"Bookkeeping subagent failed: {e}", exc_info=True)
    finally:
        try:
            await websocket.send_json({"type": "bookkeeping_complete"})
        except Exception:
            pass


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    campaign: str = Query(""),
    character: str = Query(""),
):
    await websocket.accept()
    logger.info(f"WebSocket connected: session={session_id} campaign={campaign!r} character={character!r}")

    async with ClaudeSDKClient(
        options=get_options(
            permission_mode="bypassPermissions",
            campaign=campaign,
            character=character,
        )
    ) as client:
        try:
            async for raw in websocket.iter_text():
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "error": "invalid_json"})
                    continue

                if msg.get("type") != "user_input":
                    continue

                content = msg.get("content", "").strip()
                if not content:
                    continue

                logger.info(f"[{session_id}] User input: {content[:100]}")

                # Stream main DM response, collecting text for bookkeeping handoff
                dm_response_parts: list[str] = []
                await client.query(content)

                async for message in client.receive_response():
                    process_message(message, dm_logger)

                    if not isinstance(message, AssistantMessage):
                        continue

                    for block in message.content:
                        if isinstance(block, TextBlock) and block.text:
                            dm_response_parts.append(block.text)
                            await websocket.send_json(
                                {
                                    "type": "text_chunk",
                                    "content": block.text,
                                }
                            )

                        elif isinstance(block, ToolUseBlock):
                            await websocket.send_json(
                                {
                                    "type": "tool_use",
                                    "tool_name": block.name,
                                    "tool_input": block.input,
                                    "display_name": _make_tool_display_name(block.name, block.input),
                                    "tooltip": _make_tool_tooltip(block.name, block.input),
                                    "source": "dm",
                                }
                            )

                        elif isinstance(block, ToolResultBlock):
                            if hasattr(block, "content") and block.content:
                                result_text = (
                                    block.content[0].text if hasattr(block.content[0], "text") else str(block.content)
                                )
                                try:
                                    result_data = json.loads(result_text.replace("'", '"'))
                                except (json.JSONDecodeError, AttributeError):
                                    result_data = {"raw": result_text}
                                await websocket.send_json(
                                    {
                                        "type": "tool_result",
                                        "result": result_data,
                                    }
                                )

                # Unblock the user immediately — bookkeeping runs in background
                await websocket.send_json({"type": "turn_complete"})
                logger.info(f"[{session_id}] Turn complete")

                # Bookkeeping subagent: isolated context, delegates to skills
                asyncio.create_task(
                    _forward_bookkeeping_to_ws(
                        websocket=websocket,
                        user_msg=content,
                        dm_response="\n".join(dm_response_parts),
                        campaign=campaign,
                        character=character,
                    )
                )

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: session={session_id}")
        except Exception as e:
            logger.error(f"WebSocket error [{session_id}]: {e}", exc_info=True)
            try:
                await websocket.send_json({"type": "error", "error": str(e)})
            except Exception:
                pass
