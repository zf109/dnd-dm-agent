"""Tests for utility tools - dice rolling."""

from dnd_dm_agent.tools.utility_tools import parse_dice_notation, roll_dice


# Dice rolling tests (moved from test_dice.py)
def test_roll_dice_basic():
    """Test basic dice rolling."""
    result = roll_dice("2d6+3")
    assert result["notation"] == "2d6+3"
    assert len(result["individual_rolls"]) == 2
    assert all(1 <= roll <= 6 for roll in result["individual_rolls"])
    assert result["total"] == sum(result["individual_rolls"]) + 3
    assert result["modifier"] == 3


def test_parse_dice_notation():
    """Test parsing various dice notations."""
    assert parse_dice_notation("1d20") == (1, 20, 0)
    assert parse_dice_notation("2d6+3") == (2, 6, 3)
    assert parse_dice_notation("d8-2") == (1, 8, -2)
    assert parse_dice_notation("3d4") == (3, 4, 0)