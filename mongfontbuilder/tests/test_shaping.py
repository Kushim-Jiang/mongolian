from pathlib import Path

import pytest

from mongfontbuilder.data.types import LocaleID

from fixtures import loadRawTestCases
from utils import parseAliases, parseLetter, parseWrittenUnits


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    loadRawTestCases({"eac": ["MNG"], "core": ["MNG"]}, "MNG"),
)
def test_MNG(index: str, letters: str, locale: LocaleID, goal: str, hudum_font: Path) -> None:
    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, hudum_font)
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    loadRawTestCases({"core": ["MCH"]}, "MCH"),
)
def test_MCH(index: str, letters: str, locale: LocaleID, goal: str, manchu_font: Path) -> None:
    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, manchu_font)
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    loadRawTestCases({"core": ["SIB"]}, "SIB"),
)
def test_SIB(index: str, letters: str, locale: LocaleID, goal: str, sibe_font: Path) -> None:
    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, sibe_font)
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"
