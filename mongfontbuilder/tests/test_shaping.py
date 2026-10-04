from pathlib import Path

import pytest

from mongfontbuilder.data.types import LocaleID

from fixtures import loadRawTestCases
from utils import assertWrittenUnits


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    loadRawTestCases({"eac": ["MNG"], "core": ["MNG"]}, "MNG"),
)
def test_MNG(index: str, letters: str, locale: LocaleID, goal: str, hudum_font: Path) -> None:
    assertWrittenUnits(index, letters, locale, goal, hudum_font)


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    loadRawTestCases({"core": ["MCH"]}, "MCH"),
)
def test_MCH(index: str, letters: str, locale: LocaleID, goal: str, manchu_font: Path) -> None:
    assertWrittenUnits(index, letters, locale, goal, manchu_font)


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    loadRawTestCases({"core": ["SIB"]}, "SIB"),
)
def test_SIB(index: str, letters: str, locale: LocaleID, goal: str, sibe_font: Path) -> None:
    assertWrittenUnits(index, letters, locale, goal, sibe_font)
