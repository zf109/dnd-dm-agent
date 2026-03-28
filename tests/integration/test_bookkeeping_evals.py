"""Bookkeeping scenario eval suite.

Exercises run_bookkeeping_subagent directly with fixture-based campaign state
and synthetic DM exchanges, then asserts correct post-turn file values.

Requires ANTHROPIC_API_KEY. Each test makes real API calls (~20-60s per scenario).
Run before merging changes to the campaign-guide skill or bookkeeping pipeline:

    uv run pytest tests/integration/test_bookkeeping_evals.py -v
"""

import re
import shutil
import uuid
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.parent / "fixtures"
CAMPAIGNS = Path(__file__).parent.parent.parent / "campaigns"


@pytest.fixture
def campaign_dir():
    """Create an isolated campaign directory from fixtures, yield (name, path), clean up after."""
    name = f"eval_{uuid.uuid4().hex[:8]}"
    path = CAMPAIGNS / name
    (path / "characters").mkdir(parents=True)
    yield name, path
    if path.exists():
        shutil.rmtree(path)


def _make_progress(character_line: str, beat: str = "Beat 1.1: The Job Offer") -> str:
    return (
        f"# Eval Campaign Progress\n\n"
        f"## Current Progress\n"
        f"- **Act:** Act 1 - The Brewery Investigation\n"
        f"- **Beat:** {beat} (In Progress)\n\n"
        f"## Party\n"
        f"{character_line}\n\n"
        f"## Key Decisions\n"
        f"- Accepted the brewery job\n"
    )


async def _drain(gen):
    """Consume an async generator, discarding messages."""
    async for _ in gen:
        pass


# =============================================================================
# Scenario 1: HP damage
# =============================================================================


async def test_hp_damage(campaign_dir):
    """3 damage to Thork (10/12 HP) → character file updated to 7/12."""
    name, path = campaign_dir

    shutil.copy(FIXTURES / "thork_fighter.md", path / "characters" / "thork.md")
    shutil.copy(FIXTURES / "campaign_log_empty.md", path / "campaign_log.md")
    (path / "campaign_progress.md").write_text(
        _make_progress("- **Thork Ironforge** (Mountain Dwarf Fighter 1) - HP: 10/12")
    )

    from dnd_dm_agent.claude_agent import run_bookkeeping_subagent

    await _drain(
        run_bookkeeping_subagent(
            user_msg="I swing my warhammer at the giant rat!",
            dm_response=(
                "Thork connects with his warhammer. The rat retaliates, biting into his arm "
                "for 3 damage. Thork takes 3 damage and is now at 7 HP (7/12)."
            ),
            campaign=name,
            character="thork",
        )
    )

    content = (path / "characters" / "thork.md").read_text()
    hp = re.search(r"\|\s*\*\*Hit Points\*\*\s*\|\s*(\d+)\s*/\s*(\d+)", content)
    assert hp, "HP row not found in character file"
    assert int(hp.group(1)) == 7, f"Expected current HP 7, got {hp.group(1)}"
    assert int(hp.group(2)) == 12, f"Expected max HP 12, got {hp.group(2)}"


# =============================================================================
# Scenario 2: HP healing
# =============================================================================


async def test_hp_healing(campaign_dir):
    """Healing potion (+4 HP) applied to Thork (5/12 HP) → character file updated to 9/12."""
    name, path = campaign_dir

    shutil.copy(FIXTURES / "thork_fighter_low_hp.md", path / "characters" / "thork.md")
    shutil.copy(FIXTURES / "campaign_log_empty.md", path / "campaign_log.md")
    (path / "campaign_progress.md").write_text(
        _make_progress("- **Thork Ironforge** (Mountain Dwarf Fighter 1) - HP: 5/12")
    )

    from dnd_dm_agent.claude_agent import run_bookkeeping_subagent

    await _drain(
        run_bookkeeping_subagent(
            user_msg="I drink my healing potion.",
            dm_response=(
                "Thork uncorks the minor healing potion and drinks it down. He regains 4 HP, "
                "bringing him from 5 to 9 HP (9/12)."
            ),
            campaign=name,
            character="thork",
        )
    )

    content = (path / "characters" / "thork.md").read_text()
    hp = re.search(r"\|\s*\*\*Hit Points\*\*\s*\|\s*(\d+)\s*/\s*(\d+)", content)
    assert hp, "HP row not found in character file"
    assert int(hp.group(1)) == 9, f"Expected current HP 9, got {hp.group(1)}"
    assert int(hp.group(2)) == 12, f"Expected max HP 12, got {hp.group(2)}"


# =============================================================================
# Scenario 3: Spell slot use
# =============================================================================


async def test_spell_slot_use(campaign_dir):
    """Sapphire casts Magic Missile (1st level) from full slots → used count increments to 1."""
    name, path = campaign_dir

    shutil.copy(FIXTURES / "sapphire_wizard.md", path / "characters" / "sapphire.md")
    shutil.copy(FIXTURES / "campaign_log_empty.md", path / "campaign_log.md")
    (path / "campaign_progress.md").write_text(
        _make_progress("- **Sapphire Star** (High Elf Wizard 1) - HP: 7/7\n  - Spell Slots: 1st level 0/2 used")
    )

    from dnd_dm_agent.claude_agent import run_bookkeeping_subagent

    await _drain(
        run_bookkeeping_subagent(
            user_msg="I cast Magic Missile at the rat!",
            dm_response=(
                "Sapphire expends a 1st-level spell slot to cast Magic Missile. Three glowing darts "
                "streak toward the rat. Sapphire has 1 first-level spell slot remaining (used 1 of 2)."
            ),
            campaign=name,
            character="sapphire",
        )
    )

    content = (path / "characters" / "sapphire.md").read_text()
    # Match the spell slot table row: | **1st** | 2 | 0 | 2 |
    slot = re.search(r"\*\*1st\*\*\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)", content)
    assert slot, "1st-level spell slot row not found in character file"
    total, used, remaining = int(slot.group(1)), int(slot.group(2)), int(slot.group(3))
    assert total == 2, f"Expected total slots 2, got {total}"
    assert used == 1, f"Expected used slots 1 after casting, got {used}"
    assert remaining == 1, f"Expected remaining slots 1, got {remaining}"


# =============================================================================
# Scenario 4: Beat advancement
# =============================================================================


async def test_beat_advancement(campaign_dir):
    """Completing Beat 1.1 (accept the job) → campaign_progress.md advances to Beat 1.2."""
    name, path = campaign_dir

    shutil.copy(FIXTURES / "thork_fighter.md", path / "characters" / "thork.md")
    shutil.copy(FIXTURES / "campaign_log_empty.md", path / "campaign_log.md")
    shutil.copy(FIXTURES / "campaign_guide_minimal.md", path / "campaign_guide.md")
    (path / "campaign_progress.md").write_text(
        _make_progress(
            "- **Thork Ironforge** (Mountain Dwarf Fighter 1) - HP: 10/12",
            beat="Beat 1.1: The Job Offer",
        )
    )

    from dnd_dm_agent.claude_agent import run_bookkeeping_subagent

    await _drain(
        run_bookkeeping_subagent(
            user_msg="Fine, we'll take the job. How much does it pay?",
            dm_response=(
                "Glowkindle grins with relief. 'Fifty gold pieces if you clear out every last rat and "
                "find where they came from.' Thork agrees. Beat 1.1 is now complete — the party has "
                "accepted the job and will proceed to Beat 1.2: Into the Cellar."
            ),
            campaign=name,
            character="thork",
        )
    )

    progress = (path / "campaign_progress.md").read_text()
    assert "Beat 1.1" not in progress or "Beat 1.2" in progress, (
        "Expected campaign_progress.md to advance beyond Beat 1.1"
    )
    assert "Beat 1.2" in progress, f"Expected Beat 1.2 in progress file, got:\n{progress}"
