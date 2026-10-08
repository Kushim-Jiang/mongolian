"""Shape the cases of the suites against the unified font.

The font and the cases come from ``tests/unified.py``, which composes the font once for the
session and reads the cases with the marks the font's answers call for. There are thousands
of cases and each one is shaped against the composed font, so the console is told where the
run has come; run pytest with `-s` to see it:

    uv run pytest tests/test_unified.py -s
"""

from collections import Counter
from pathlib import Path

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from ufoLib2 import Font

from mongfontbuilder.data.types import LocaleID

from unified import (
    CASES,
    LANGUAGE,
    VERTICAL_MARGIN,
    buildUnifiedFont,
    caseIndexes,
    composedUFO,
    inkBox,
    languageOf,
)
from utils import assertWrittenUnits


@pytest.fixture(scope="session")
def unifiedFont() -> Path:
    """The unified font, composed once for the whole session.

    Composing the font and compiling it takes a while, so the whole session shares one
    build; the composed UFO and OTF are left in ``temp/``.
    """

    return buildUnifiedFont()


def test_unified(unifiedFont: Path) -> None:
    """The build is a font at both ends of it: the UFO composes glyphs and the OTF is compiled.

    The fixture answers with the two paths whether it composed the font or found it, so what
    is asserted here is not that they exist but that they open and carry what the cases
    shape through.
    """

    assert Font.open(composedUFO).keys()
    assert "GSUB" in TTFont(unifiedFont)


@pytest.mark.parametrize("script", ["Mong", "Hani", "Zyyy"])
def test_vertical_boxes(unifiedFont: Path, script: str) -> None:
    """An upright mark is read in its drawing plus the margin, whatever the script of the run.

    The box is the vertical metrics of the glyph, so a vertical line shaped with no feature
    asked for gives it: the mark advances by its drawing and `VERTICAL_MARGIN` at each end,
    and its drawing begins `VERTICAL_MARGIN` into that advance. A layout resolves punctuation
    to the script of the text around it, or to none, so the box is checked under each.
    """

    source = Font.open(composedUFO)
    assert "vpal" not in {
        record.FeatureTag for record in TTFont(unifiedFont)["GPOS"].table.FeatureList.FeatureRecord
    }
    font = hb.Font(hb.Face(unifiedFont.read_bytes()))  # type: ignore
    forms = [name for name in source.keys() if name.endswith(".vert")]
    assert forms
    for name in forms:
        _, yMin, _, yMax = inkBox(source[name])
        (codePoint,) = source[name.removesuffix(".vert")].unicodes
        buffer = hb.Buffer()  # type: ignore
        buffer.add_codepoints([codePoint])
        buffer.direction = "ttb"
        buffer.script = script
        hb.shape(font, buffer)  # type: ignore
        (position,) = buffer.glyph_positions
        assert -position.y_advance == yMax - yMin + 2 * VERTICAL_MARGIN, name
        assert -position.y_offset == yMax + VERTICAL_MARGIN, name


# The cases of the suites, and how far a run of them has come. There are thousands of
# cases and each one is shaped against the composed font, so the console is told where the
# run is; run pytest with `-s` to see it.
doneCases = Counter[str]()
totalCases = Counter[str](index.split(" > ")[0] for index in caseIndexes(CASES))


def report(index: str, result: str) -> None:
    """Tell the console where the run of the suites has come."""

    suite, name = index.split(" > ", 1)
    doneCases[suite] += 1
    print(f"{suite} {doneCases[suite]}/{totalCases[suite]} {name}: {result}", flush=True)


@pytest.mark.parametrize(
    ("index", "letters", "locale", "goal"),
    CASES,
)
def test_conformance(
    index: str,
    letters: str,
    locale: LocaleID,
    goal: str,
    unifiedFont: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def tell(index: str, answer: str) -> None:
        with capsys.disabled():
            report(index, answer)

    assertWrittenUnits(
        index, letters, locale, goal, unifiedFont, languageOf(LANGUAGE[locale]), tell
    )
