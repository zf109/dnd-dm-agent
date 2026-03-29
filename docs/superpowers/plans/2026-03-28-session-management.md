# Session Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the flat campaign/character dropdown with a campaign browser CRUD interface and wire up resume vs. new-session init messages.

**Architecture:** Backend adds three new endpoints (GET /api/templates, POST /api/campaigns, DELETE /api/campaigns/{instance}) and enriches the existing GET /api/campaigns to return structured instance objects. Frontend replaces `SessionSetup.tsx` with `CampaignBrowser.tsx` that shows in-progress instances with Resume/Delete and a "Start New Adventure" form.

**Tech Stack:** Python/FastAPI (server.py), React/TypeScript (Vite), pytest (backend tests)

---

## File Map

**Backend (modify):**
- `dnd_dm_agent/server.py` — add/enrich REST endpoints
- `tests/test_server.py` — new file, unit tests for all 4 campaign endpoints

**Frontend (create/modify/delete):**
- `frontend/src/components/CampaignBrowser.tsx` — new component, replaces SessionSetup
- `frontend/src/App.tsx` — update SessionConfig type, handleStart signature, init message
- `frontend/src/App.css` — add campaign browser styles
- `frontend/src/components/SessionSetup.tsx` — delete at the end

---

## Task 1: Enrich GET /api/campaigns

**Files:**
- Modify: `dnd_dm_agent/server.py`
- Create: `tests/test_server.py`

The endpoint currently returns `{"instances": ["a_most_potent_brew_thork_adventure", ...]}`. It must return structured objects:
```json
{
  "instances": [
    {
      "name": "a_most_potent_brew_thork_adventure",
      "display_name": "A Most Potent Brew — Thork Adventure",
      "character": "Thork Ironforge · Mountain Dwarf Fighter 1",
      "beat": "Act 1 · Beat 1.3: The Corrupted Vats"
    }
  ]
}
```

Parsing rules from `campaign_progress.md`:
- **display_name**: read `**Template:**` and `**Instance:**` lines, title-case and join with ` — `
- **character**: first line matching `- **Name** (Class)` in `## Party` → `"Name · Class"`
- **beat**: `- **Beat:** <text>` and `- **Act:** Act N` → `"Act N · <beat text>"`. Strip trailing ` (In Progress)` etc. Fall back to `""` if not found.

- [ ] **Step 1: Write failing tests**

Create `tests/test_server.py`:

```python
"""Tests for campaign REST endpoints."""

import shutil
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from dnd_dm_agent.server import app, PROJECT_ROOT

client = TestClient(app)

CAMPAIGNS = PROJECT_ROOT / "campaigns"


@pytest.fixture
def instance_dir(tmp_path, monkeypatch):
    """Patch PROJECT_ROOT so endpoints use a temp campaigns dir."""
    import dnd_dm_agent.server as srv
    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    inst = tmp_path / "campaigns" / "a_most_potent_brew_thork_adventure"
    (inst / "characters").mkdir(parents=True)
    (inst / "campaign_progress.md").write_text(
        "# A Most Potent Brew - thork_adventure\n\n"
        "**Instance:** thork_adventure\n"
        "**Template:** a_most_potent_brew\n"
        "**Created:** 2026-03-28\n\n"
        "## Current Progress\n"
        "- **Act:** Act 1 - The Brewery Investigation\n"
        "- **Beat:** Beat 1.2: Into the Cellar\n\n"
        "## Party\n"
        "- **Thork Ironforge** (Mountain Dwarf Fighter 1) - HP: 10/12\n\n"
        "## Key Decisions\n"
    )
    return tmp_path


def test_list_campaigns_enriched(instance_dir):
    resp = client.get("/api/campaigns")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["instances"]) == 1
    inst = data["instances"][0]
    assert inst["name"] == "a_most_potent_brew_thork_adventure"
    assert inst["display_name"] == "A Most Potent Brew — Thork Adventure"
    assert inst["character"] == "Thork Ironforge · Mountain Dwarf Fighter 1"
    assert inst["beat"] == "Act 1 · Beat 1.2: Into the Cellar"


def test_list_campaigns_empty(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv
    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    resp = client.get("/api/campaigns")
    assert resp.status_code == 200
    assert resp.json() == {"instances": []}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_server.py::test_list_campaigns_enriched tests/test_server.py::test_list_campaigns_empty -v
```

Expected: FAIL — `test_list_campaigns_enriched` fails because response is a list of strings, not objects.

- [ ] **Step 3: Add `_parse_instance_meta` helper and update the endpoint**

In `dnd_dm_agent/server.py`, add after imports:

```python
import re
import shutil
```

Add helper function before the REST endpoints section:

```python
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
    beat_m = re.search(r"- \*\*Beat:\*\*\s*(.+?)(?:\s*[\(\-].*)?$", text, re.MULTILINE)
    if beat_m:
        beat_text = beat_m.group(1).strip()
        beat = f"Act {act_m.group(1)} \u00b7 {beat_text}" if act_m else beat_text
    else:
        beat = ""

    return {"name": name, "display_name": display_name, "character": character, "beat": beat}
```

Replace the `list_campaigns` endpoint:

```python
@app.get("/api/campaigns")
async def list_campaigns():
    campaigns_dir = PROJECT_ROOT / "campaigns"
    if not campaigns_dir.exists():
        return {"instances": []}
    dirs = sorted(d for d in campaigns_dir.iterdir() if d.is_dir())
    return {"instances": [_parse_instance_meta(d) for d in dirs]}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_server.py::test_list_campaigns_enriched tests/test_server.py::test_list_campaigns_empty -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dnd_dm_agent/server.py tests/test_server.py
git commit -m "feat: enrich GET /api/campaigns with instance metadata"
```

---

## Task 2: Add GET /api/templates endpoint

**Files:**
- Modify: `dnd_dm_agent/server.py`
- Modify: `tests/test_server.py`

Returns available campaign templates with their pregenerated characters:
```json
{
  "templates": [
    {
      "name": "a_most_potent_brew",
      "display_name": "A Most Potent Brew",
      "characters": [
        {"name": "dwarf_fighter", "display_name": "Dwarf Fighter"},
        {"name": "elf_wizard", "display_name": "Elf Wizard"},
        {"name": "halfling_wizard", "display_name": "Halfling Wizard"}
      ]
    }
  ]
}
```

- [ ] **Step 1: Write failing test**

Append to `tests/test_server.py`:

```python
@pytest.fixture
def templates_dir(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv
    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    pregen = tmp_path / "available_campaigns" / "a_most_potent_brew" / "pregenerated_characters"
    pregen.mkdir(parents=True)
    (pregen / "dwarf_fighter.md").write_text("# Dwarf Fighter")
    (pregen / "elf_wizard.md").write_text("# Elf Wizard")
    return tmp_path


def test_list_templates(templates_dir):
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["templates"]) == 1
    t = data["templates"][0]
    assert t["name"] == "a_most_potent_brew"
    assert t["display_name"] == "A Most Potent Brew"
    char_names = [c["name"] for c in t["characters"]]
    assert "dwarf_fighter" in char_names
    assert "elf_wizard" in char_names


def test_list_templates_empty(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv
    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    resp = client.get("/api/templates")
    assert resp.status_code == 200
    assert resp.json() == {"templates": []}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_server.py::test_list_templates -v
```

Expected: FAIL — 404 (endpoint doesn't exist yet)

- [ ] **Step 3: Add endpoint to server.py**

After the `list_campaigns` endpoint:

```python
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
                {"name": f.stem, "display_name": f.stem.replace("_", " ").title()}
                for f in pregen.glob("*.md")
            )
        result.append({
            "name": d.name,
            "display_name": d.name.replace("_", " ").title(),
            "characters": characters,
        })
    return {"templates": result}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_server.py::test_list_templates tests/test_server.py::test_list_templates_empty -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dnd_dm_agent/server.py tests/test_server.py
git commit -m "feat: add GET /api/templates endpoint"
```

---

## Task 3: Add POST /api/campaigns endpoint

**Files:**
- Modify: `dnd_dm_agent/server.py`
- Modify: `tests/test_server.py`

Creates a campaign instance and copies the selected pregenerated character into the instance's `characters/` directory.

Request body:
```json
{"template": "a_most_potent_brew", "character": "dwarf_fighter"}
```

Response (201):
```json
{
  "instance": "a_most_potent_brew_dwarf_fighter",
  "character": "dwarf_fighter"
}
```

Error (409) if instance already exists. Error (400) if template not found. Instance name = `{template}_{character}`.

- [ ] **Step 1: Write failing test**

Append to `tests/test_server.py`:

```python
@pytest.fixture
def create_env(tmp_path, monkeypatch):
    """Temp dir with one template and one pregenerated character."""
    import dnd_dm_agent.server as srv
    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    # Also patch campaign_instance_tools PROJECT_ROOT via server's imported create_campaign_instance
    import dnd_dm_agent.tools.campaign_instance_tools as cit
    monkeypatch.setattr(cit, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(cit, "CAMPAIGNS_DIR", tmp_path / "campaigns")
    pregen = tmp_path / "available_campaigns" / "a_most_potent_brew" / "pregenerated_characters"
    pregen.mkdir(parents=True)
    (pregen / "dwarf_fighter.md").write_text("# Dwarf Fighter\nHP: 12/12")
    return tmp_path


def test_create_campaign(create_env):
    resp = client.post("/api/campaigns", json={"template": "a_most_potent_brew", "character": "dwarf_fighter"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["instance"] == "a_most_potent_brew_dwarf_fighter"
    assert data["character"] == "dwarf_fighter"
    # Character file was copied
    char_file = create_env / "campaigns" / "a_most_potent_brew_dwarf_fighter" / "characters" / "dwarf_fighter.md"
    assert char_file.exists()
    assert "HP: 12/12" in char_file.read_text()


def test_create_campaign_duplicate(create_env):
    client.post("/api/campaigns", json={"template": "a_most_potent_brew", "character": "dwarf_fighter"})
    resp = client.post("/api/campaigns", json={"template": "a_most_potent_brew", "character": "dwarf_fighter"})
    assert resp.status_code == 409


def test_create_campaign_bad_template(create_env):
    resp = client.post("/api/campaigns", json={"template": "nonexistent", "character": "dwarf_fighter"})
    assert resp.status_code == 400
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_server.py::test_create_campaign tests/test_server.py::test_create_campaign_duplicate tests/test_server.py::test_create_campaign_bad_template -v
```

Expected: FAIL — 404 (endpoint doesn't exist)

- [ ] **Step 3: Add Pydantic model and endpoint to server.py**

Add after imports:

```python
from pydantic import BaseModel

class CreateCampaignRequest(BaseModel):
    template: str
    character: str
```

Add endpoint after `list_templates`:

```python
@app.post("/api/campaigns", status_code=201)
async def create_campaign(req: CreateCampaignRequest):
    from .tools.campaign_instance_tools import create_campaign_instance

    # Validate template exists
    template_path = PROJECT_ROOT / "available_campaigns" / req.template
    if not template_path.exists():
        raise HTTPException(status_code=400, detail=f"Template '{req.template}' not found")

    # Instance name = template_character
    instance_name = req.character
    result = create_campaign_instance(req.template, instance_name)

    if result["status"] == "error":
        if "already exists" in result.get("error_message", ""):
            raise HTTPException(status_code=409, detail=result["error_message"])
        raise HTTPException(status_code=500, detail=result["error_message"])

    # Copy pregenerated character file into instance characters dir
    pregen_src = template_path / "pregenerated_characters" / f"{req.character}.md"
    if pregen_src.exists():
        instance_dir = PROJECT_ROOT / "campaigns" / f"{req.template}_{instance_name}"
        dst = instance_dir / "characters" / f"{req.character}.md"
        dst.write_text(pregen_src.read_text())

    return {"instance": f"{req.template}_{instance_name}", "character": req.character}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_server.py::test_create_campaign tests/test_server.py::test_create_campaign_duplicate tests/test_server.py::test_create_campaign_bad_template -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dnd_dm_agent/server.py tests/test_server.py
git commit -m "feat: add POST /api/campaigns endpoint with character copy"
```

---

## Task 4: Add DELETE /api/campaigns/{instance} endpoint

**Files:**
- Modify: `dnd_dm_agent/server.py`
- Modify: `tests/test_server.py`

Removes the campaign instance directory entirely. Returns 204. Returns 404 if not found.

- [ ] **Step 1: Write failing test**

Append to `tests/test_server.py`:

```python
@pytest.fixture
def deletable_instance(tmp_path, monkeypatch):
    import dnd_dm_agent.server as srv
    monkeypatch.setattr(srv, "PROJECT_ROOT", tmp_path)
    inst = tmp_path / "campaigns" / "a_most_potent_brew_thork_adventure"
    (inst / "characters").mkdir(parents=True)
    (inst / "campaign_progress.md").write_text("# test")
    return tmp_path


def test_delete_campaign(deletable_instance):
    resp = client.delete("/api/campaigns/a_most_potent_brew_thork_adventure")
    assert resp.status_code == 204
    assert not (deletable_instance / "campaigns" / "a_most_potent_brew_thork_adventure").exists()


def test_delete_campaign_not_found(deletable_instance):
    resp = client.delete("/api/campaigns/nonexistent_campaign")
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_server.py::test_delete_campaign tests/test_server.py::test_delete_campaign_not_found -v
```

Expected: FAIL — 404 (endpoint doesn't exist)

- [ ] **Step 3: Add endpoint to server.py**

```python
@app.delete("/api/campaigns/{campaign_instance}", status_code=204)
async def delete_campaign(campaign_instance: str):
    instance_path = PROJECT_ROOT / "campaigns" / campaign_instance
    if not instance_path.exists() or not instance_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Instance '{campaign_instance}' not found")
    shutil.rmtree(instance_path)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_server.py -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add dnd_dm_agent/server.py tests/test_server.py
git commit -m "feat: add DELETE /api/campaigns/{instance} endpoint"
```

---

## Task 5: Update App.tsx — SessionConfig and init message

**Files:**
- Modify: `frontend/src/App.tsx`

Add `isResume: boolean` to `SessionConfig`. Update `handleStart` to accept it. Update the init message effect to send a different message when `isResume` is true (per ADR-011).

- [ ] **Step 1: Update SessionConfig interface**

In `frontend/src/App.tsx`, replace:

```typescript
interface SessionConfig {
  campaign: string;
  character: string;
}
```

with:

```typescript
interface SessionConfig {
  campaign: string;
  character: string;
  isResume: boolean;
}
```

- [ ] **Step 2: Update handleStart callback**

Replace:

```typescript
  const handleStart = useCallback((campaign: string, character: string) => {
    const config = { campaign, character };
    saveSession(config);
    setSession(config);
  }, []);
```

with:

```typescript
  const handleStart = useCallback((campaign: string, character: string, isResume: boolean) => {
    const config = { campaign, character, isResume };
    saveSession(config);
    setSession(config);
  }, []);
```

- [ ] **Step 3: Update init message effect in GameView**

Replace the init `useEffect` block (the one with `sendMessage` and `"Session started."`) in `GameView`:

```typescript
  useEffect(() => {
    if (wsStatus !== 'connected' || hasInitialized.current) return;
    hasInitialized.current = true;
    if (isRestoredSession.current) return;
    const campaignLabel = session.campaign.replace(/_/g, ' ');
    const characterLabel = activeCharacter.replace(/_/g, ' ');
    dispatch({ type: 'ADD_SYSTEM_MESSAGE', content: `Campaign: ${campaignLabel}  ·  Character: ${characterLabel}` });
    const initContent = session.isResume
      ? `Resuming session. Campaign: "${campaignLabel}". Active character: "${characterLabel}". Use the campaign-guide skill to load current state and welcome the player back with a brief recap of where they left off before asking what they'd like to do.`
      : `Session started. Campaign: "${campaignLabel}". Active character: "${characterLabel}". Please load the campaign using the campaign-guide skill and greet the player in character as the DM.`;
    sendMessage({ type: 'user_input', content: initContent });
  }, [wsStatus, session.campaign, session.isResume, activeCharacter, sendMessage]);
```

- [ ] **Step 4: Verify TypeScript still compiles**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors (the CampaignBrowser import will fail until Task 6 — comment out or ignore that one error for now)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: add isResume to SessionConfig and wire resume init message"
```

---

## Task 6: Create CampaignBrowser.tsx

**Files:**
- Create: `frontend/src/components/CampaignBrowser.tsx`
- Modify: `frontend/src/App.tsx` — swap import

The component:
- Fetches `/api/campaigns` on mount → shows in-progress list
- Fetches `/api/templates` on mount → populates "Start New Adventure" form
- Resume row: calls `onStart(instance.name, characterStem(instance.character), true)`
- Delete row: shows inline confirm, then calls `DELETE /api/campaigns/{name}` and refreshes
- Create form: POST `/api/campaigns`, then calls `onStart(newInstance, character, false)`

`characterStem` helper: the `character` field in API response is `"Thork Ironforge · Mountain Dwarf Fighter 1"`. The actual file stem (needed for the WS query) is `req.character` = `"dwarf_fighter"` — BUT the instance's characters dir contains one file whose stem IS the character used in `POST /api/campaigns`. So on Resume, the character file stem is whatever exists in `characters/`. The simplest approach: the `character` display field is only for display; the WS needs a filename. We need to return the character filename stem separately from the API.

**Update the enriched GET /api/campaigns response to include a `character_file` field** (the stem of the first `.md` in `characters/`):

- [ ] **Step 1: Add `character_file` to `_parse_instance_meta` in server.py**

In the `_parse_instance_meta` function, after building the `character` display string, add:

```python
    # character_file: stem of first file in characters/ dir
    chars_dir = instance_dir / "characters"
    char_files = sorted(chars_dir.glob("*.md")) if chars_dir.exists() else []
    character_file = char_files[0].stem if char_files else ""
```

Update the return dict:

```python
    return {
        "name": name,
        "display_name": display_name,
        "character": character,
        "character_file": character_file,
        "beat": beat,
    }
```

Also update `test_list_campaigns_enriched` in `tests/test_server.py` to add the character file:

In the `instance_dir` fixture, create a character file:
```python
    (inst / "characters" / "thork.md").write_text("# Thork")
```

Add assertion:
```python
    assert inst["character_file"] == "thork"
```

Re-run:
```bash
uv run pytest tests/test_server.py::test_list_campaigns_enriched -v
```

Expected: PASS

- [ ] **Step 2: Commit server fix**

```bash
git add dnd_dm_agent/server.py tests/test_server.py
git commit -m "feat: add character_file to campaign instance metadata"
```

- [ ] **Step 3: Create CampaignBrowser.tsx**

Create `frontend/src/components/CampaignBrowser.tsx`:

```typescript
import { useState, useEffect, useCallback } from 'react';

interface CampaignInstance {
  name: string;
  display_name: string;
  character: string;
  character_file: string;
  beat: string;
}

interface Character {
  name: string;
  display_name: string;
}

interface Template {
  name: string;
  display_name: string;
  characters: Character[];
}

interface Props {
  onStart: (campaign: string, character: string, isResume: boolean) => void;
}

export function CampaignBrowser({ onStart }: Props) {
  const [instances, setInstances] = useState<CampaignInstance[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [selectedCharacter, setSelectedCharacter] = useState('');
  const [creating, setCreating] = useState(false);

  const refresh = useCallback(() => {
    setLoading(true);
    Promise.all([
      fetch('/api/campaigns').then((r) => r.json()),
      fetch('/api/templates').then((r) => r.json()),
    ])
      .then(([campaigns, templateData]) => {
        setInstances(campaigns.instances ?? []);
        setTemplates(templateData.templates ?? []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Reset character when template changes
  useEffect(() => { setSelectedCharacter(''); }, [selectedTemplate]);

  const activeTemplate = templates.find((t) => t.name === selectedTemplate);

  const handleDelete = async (name: string) => {
    await fetch(`/api/campaigns/${name}`, { method: 'DELETE' });
    setConfirmDelete(null);
    refresh();
  };

  const handleCreate = async () => {
    if (!selectedTemplate || !selectedCharacter || creating) return;
    setCreating(true);
    try {
      const resp = await fetch('/api/campaigns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ template: selectedTemplate, character: selectedCharacter }),
      });
      if (!resp.ok) return;
      const data = await resp.json();
      onStart(data.instance, data.character, false);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="browser-overlay">
      <div className="browser">

        <div className="browser-header">
          <h1 className="browser-title">⚔ D&amp;D DM Agent</h1>
          <p className="browser-subtitle">Choose an adventure or begin a new one</p>
        </div>

        <div className="section-label">Adventures in Progress</div>

        {loading ? (
          <div className="browser-skeleton">
            <div className="skeleton-row" />
            <div className="skeleton-row" />
          </div>
        ) : instances.length === 0 ? (
          <div className="empty-state">No adventures in progress</div>
        ) : (
          <div className="campaign-list">
            {instances.map((inst) => (
              <div
                key={inst.name}
                className={`campaign-row${confirmDelete === inst.name ? ' confirming' : ''}`}
              >
                <div className="campaign-info">
                  <div className="campaign-name">{inst.display_name}</div>
                  <div className="campaign-meta">
                    {inst.character}
                    {inst.beat && <><span className="sep">·</span><span className="beat">{inst.beat}</span></>}
                  </div>
                </div>

                {confirmDelete === inst.name ? (
                  <div className="confirm-prompt">
                    Delete this adventure?
                    <button className="btn-confirm-yes" onClick={() => handleDelete(inst.name)}>Yes</button>
                    <button className="btn-confirm-cancel" onClick={() => setConfirmDelete(null)}>Cancel</button>
                  </div>
                ) : (
                  <div className="campaign-actions">
                    <button
                      className="btn-resume"
                      onClick={() => onStart(inst.name, inst.character_file, true)}
                    >
                      Resume
                    </button>
                    <button className="btn-delete" onClick={() => setConfirmDelete(inst.name)}>✕</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="browser-divider" />

        <div className="section-label">Start New Adventure</div>

        <div className="new-campaign">
          <div className="form-row">
            <select
              className="form-select"
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
            >
              <option value="">— Select a campaign —</option>
              {templates.map((t) => (
                <option key={t.name} value={t.name}>{t.display_name}</option>
              ))}
            </select>
            <select
              className="form-select"
              value={selectedCharacter}
              onChange={(e) => setSelectedCharacter(e.target.value)}
              disabled={!selectedTemplate}
            >
              <option value="">— Select a character —</option>
              {(activeTemplate?.characters ?? []).map((c) => (
                <option key={c.name} value={c.name}>{c.display_name}</option>
              ))}
            </select>
          </div>
          <button
            className="btn-start"
            disabled={!selectedTemplate || !selectedCharacter || creating}
            onClick={handleCreate}
          >
            {creating ? 'Starting…' : 'Start New Adventure'}
          </button>
        </div>

      </div>
    </div>
  );
}
```

- [ ] **Step 4: Update App.tsx to use CampaignBrowser**

Replace the `SessionSetup` import:

```typescript
import { CampaignBrowser } from './components/CampaignBrowser';
```

Replace the render in `App`:

```typescript
  if (!session) {
    return <CampaignBrowser onStart={handleStart} />;
  }
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/CampaignBrowser.tsx frontend/src/App.tsx
git commit -m "feat: add CampaignBrowser component replacing SessionSetup"
```

---

## Task 7: Add CSS for CampaignBrowser

**Files:**
- Modify: `frontend/src/App.css`

Add the campaign browser styles. These match the design tokens from ADR-012 and the mockup.

- [ ] **Step 1: Append CSS to App.css**

Append to the end of `frontend/src/App.css`:

```css
/* ── Campaign Browser ── */
.browser-overlay {
  position: fixed;
  inset: 0;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  overflow-y: auto;
}

.browser {
  width: 100%;
  max-width: 640px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.browser-header {
  padding: 32px 32px 24px;
  border-bottom: 1px solid var(--border-color);
  text-align: center;
}

.browser-title {
  font-family: var(--font-serif);
  font-size: 1.6rem;
  color: var(--accent-gold);
  letter-spacing: 0.05em;
  margin-bottom: 6px;
}

.browser-subtitle {
  font-family: var(--font-serif-body);
  font-size: 0.85rem;
  color: var(--text-muted);
  font-style: italic;
}

.section-label {
  font-family: var(--font-serif);
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent-gold-dim);
  padding: 20px 32px 10px;
}

.campaign-list {
  padding: 0 24px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.campaign-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-panel);
  transition: border-color 0.15s;
}

.campaign-row:hover {
  border-color: var(--accent-gold-dim);
}

.campaign-row.confirming {
  border-color: rgba(192, 57, 43, 0.27);
}

.campaign-info {
  flex: 1;
  min-width: 0;
}

.campaign-name {
  font-family: var(--font-serif);
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.campaign-meta {
  font-family: var(--font-serif-body);
  font-size: 0.75rem;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.campaign-meta .beat { font-style: italic; }
.campaign-meta .sep { margin: 0 6px; opacity: 0.4; }

.campaign-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-resume {
  padding: 6px 16px;
  font-family: var(--font-serif);
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  color: var(--accent-gold);
  background: transparent;
  border: 1px solid var(--accent-gold);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-resume:hover { background: rgba(201, 168, 76, 0.12); }

.btn-delete {
  padding: 6px 10px;
  font-size: 0.72rem;
  color: var(--text-muted);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}

.btn-delete:hover {
  color: #c0392b;
  border-color: rgba(192, 57, 43, 0.27);
}

.confirm-prompt {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  color: #c0392b;
  flex-shrink: 0;
}

.btn-confirm-yes {
  padding: 4px 10px;
  font-size: 0.72rem;
  color: #c0392b;
  background: transparent;
  border: 1px solid #c0392b;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm-cancel {
  padding: 4px 10px;
  font-size: 0.72rem;
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
}

.empty-state {
  padding: 28px 32px;
  text-align: center;
  font-family: var(--font-serif-body);
  font-style: italic;
  color: var(--text-muted);
  font-size: 0.85rem;
  border: 1px dashed var(--border-color);
  border-radius: 6px;
  margin: 0 24px 8px;
}

.browser-skeleton {
  padding: 0 24px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.skeleton-row {
  height: 62px;
  border-radius: 6px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.browser-divider {
  height: 1px;
  background: var(--border-color);
  margin: 12px 0;
}

.new-campaign {
  padding: 8px 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.form-select {
  flex: 1;
  padding: 9px 12px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 0.82rem;
  appearance: none;
  cursor: pointer;
  transition: border-color 0.15s;
}

.form-select:focus {
  outline: none;
  border-color: var(--accent-gold-dim);
}

.form-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-start {
  width: 100%;
  padding: 11px;
  font-family: var(--font-serif);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  color: var(--bg-primary);
  background: var(--accent-gold);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-start:hover { opacity: 0.88; }
.btn-start:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
```

- [ ] **Step 2: Visually check in browser**

Start dev server and verify the browser renders correctly at http://localhost:5173:

```bash
cd frontend && npm run dev
```

Verify:
- Header shows "⚔ D&D DM Agent"
- In-progress list populates (or shows empty state)
- "Start New Adventure" form has template/character dropdowns
- Skeleton animation appears while loading

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.css
git commit -m "feat: add campaign browser CSS styles"
```

---

## Task 8: Delete SessionSetup.tsx and run full test suite

**Files:**
- Delete: `frontend/src/components/SessionSetup.tsx`
- Run: all tests

- [ ] **Step 1: Delete SessionSetup.tsx**

```bash
rm frontend/src/components/SessionSetup.tsx
```

- [ ] **Step 2: Verify no remaining references**

```bash
grep -r "SessionSetup" frontend/src/
```

Expected: no output

- [ ] **Step 3: TypeScript compile check**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors

- [ ] **Step 4: Run backend tests**

```bash
uv run pytest tests/test_server.py tests/test_campaign_instance_tools.py tests/test_utility_tools.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: delete SessionSetup.tsx — replaced by CampaignBrowser"
```

---

## Self-Review Checklist

**Spec coverage (ADR-011 + ADR-012):**
- [x] Read (list instances) — Task 1
- [x] Create (new instance from template + character copy) — Task 3
- [x] Delete (instance removal, inline confirm) — Task 4, Task 6
- [x] Update (gameplay itself, no UI action needed) — not changed, correct
- [x] Resume sends recap init message — Task 5
- [x] New session sends existing init message — Task 5
- [x] SessionSetup.tsx deleted — Task 8
- [x] No character re-selection on resume — CampaignBrowser uses stored character_file
- [x] Inline delete confirm, no modal — Task 6
- [x] Empty state — Task 6
- [x] Skeleton rows during load — Task 6 + 7
- [x] Visual style matches design tokens — Task 7
- [x] Do NOT store chat history server-side (ADR-011 constraint) — unchanged, correct
- [x] Do NOT modify campaign-guide skill — not touched
- [x] Do NOT merge instance identity into template structure (ADR-004) — not touched

**Type consistency:**
- `onStart(campaign: string, character: string, isResume: boolean)` — same signature in App.tsx and CampaignBrowser.tsx
- `CampaignInstance.character_file` — added to server.py in Task 6 Step 1 before used in CampaignBrowser.tsx

**No placeholders:** All steps have complete code.
