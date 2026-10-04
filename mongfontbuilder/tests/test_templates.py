import sys
from subprocess import run

import pytest

from mongfontbuilder.data.types import LocaleID

from fixtures import loadRawTestCases
from unified import LANGUAGE, languageOf
from utils import assertWrittenUnits, repo, tempDir

targeted = sys.platform == "darwin"
fontPath = tempDir / "HudumTemplate-Regular.otf"

if targeted and not fontPath.exists():
    run(
        ["uv", "run", "glyphs", "export", "--output", tempDir, repo / "templates" / "hudum.glyphs"],
        check=True,
    )

testCases = loadRawTestCases({"eac": ["MNG"], "core": ["MNG"]}) if fontPath.exists() else []


@pytest.mark.skipif(not targeted, reason="The test font can only be built on macOS.")
@pytest.mark.parametrize(("index", "letters", "locale", "goal"), testCases)
def test_MNG(index: str, letters: str, locale: LocaleID, goal: str) -> None:
    assertWrittenUnits(index, letters, locale, goal, fontPath, languageOf(LANGUAGE[locale]))
