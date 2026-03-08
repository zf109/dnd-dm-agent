"""FastAPI WebSocket server exposing the D&D DM Agent."""

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock

from .claude_agent import get_options, process_message, run_bookkeeping_subagent
from .logging_config import logger, dm_logger, bookkeeping_logger

PROJECT_ROOT = Path(__file__).parent.parent

app = FastAPI(title="D&D DM Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    instances = [d.name for d in campaigns_dir.iterdir() if d.is_dir()]
    return {"instances": sorted(instances)}


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


def _make_tool_display_name(tool_name: str) -> str:
    """Convert internal tool name to user-friendly display string."""
    names = {
        "mcp__dnd__roll_dice": "rolling dice",
        "mcp__dnd__create_campaign_instance": "creating campaign",
        "Read": "reading files",
        "Write": "writing files",
        "Edit": "updating files",
        "Grep": "searching knowledge",
        "Glob": "finding files",
        "Skill": "consulting knowledge",
    }
    return names.get(tool_name, tool_name.lower().replace("_", " "))


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
                        await websocket.send_json({
                            "type": "tool_use",
                            "tool_name": block.name,
                            "tool_input": block.input,
                            "display_name": _make_tool_display_name(block.name),
                        })
                    except Exception:
                        pass  # WebSocket may have closed
    except Exception as e:
        bookkeeping_logger.error(f"Bookkeeping subagent failed: {e}", exc_info=True)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    campaign: str = Query(""),
    character: str = Query(""),
):
    await websocket.accept()
    logger.info(f"WebSocket connected: session={session_id} campaign={campaign!r} character={character!r}")

    async with ClaudeSDKClient(options=get_options(
        permission_mode="bypassPermissions",
        campaign=campaign,
        character=character,
    )) as client:
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
                            await websocket.send_json({
                                "type": "text_chunk",
                                "content": block.text,
                            })

                        elif isinstance(block, ToolUseBlock):
                            await websocket.send_json({
                                "type": "tool_use",
                                "tool_name": block.name,
                                "tool_input": block.input,
                                "display_name": _make_tool_display_name(block.name),
                            })
                            if block.name == "Read":
                                file_path = block.input.get("file_path", "")
                                if "/characters/" in str(file_path) and str(file_path).endswith(".md"):
                                    await websocket.send_json({"type": "open_character_sheet"})

                        elif isinstance(block, ToolResultBlock):
                            if hasattr(block, "content") and block.content:
                                result_text = (
                                    block.content[0].text
                                    if hasattr(block.content[0], "text")
                                    else str(block.content)
                                )
                                try:
                                    result_data = json.loads(result_text.replace("'", '"'))
                                except (json.JSONDecodeError, AttributeError):
                                    result_data = {"raw": result_text}
                                await websocket.send_json({
                                    "type": "tool_result",
                                    "result": result_data,
                                })

                # Unblock the user immediately — bookkeeping runs in background
                await websocket.send_json({"type": "turn_complete"})
                logger.info(f"[{session_id}] Turn complete")

                # Bookkeeping subagent: isolated context, delegates to skills
                asyncio.create_task(_forward_bookkeeping_to_ws(
                    websocket=websocket,
                    user_msg=content,
                    dm_response="\n".join(dm_response_parts),
                    campaign=campaign,
                    character=character,
                ))

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: session={session_id}")
        except Exception as e:
            logger.error(f"WebSocket error [{session_id}]: {e}", exc_info=True)
            try:
                await websocket.send_json({"type": "error", "error": str(e)})
            except Exception:
                pass
