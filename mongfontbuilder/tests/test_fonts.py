"""The source fonts draw the characters their writing systems write.

The characters of the script that are not letters — the marks and the digits — are drawn in
the source fonts rather than composed, so nothing in the composition would notice one that a
writing system is given by the data and its font does not draw. `sibe.ufo` has no template of
its own and draws none of them; the unified font is the one the documentation's written
forms come from, and draws them for every writing system.
"""

import pytest
from ufoLib2 import Font

from mongfontbuilder import data
from mongfontbuilder.data.types import LocaleID
from utils import fontsDir

FONTS: dict[str, list[LocaleID]] = {
    "hudum.ufo": ["MNG"],
    "manchu.ufo": ["MCH"],
    "unified.ufo": [*data.locales],
}
ALL_FONTS = [*FONTS, "sibe.ufo"]


def codePoints(fontName: str) -> set[int]:
    font = Font.open(fontsDir / fontName)
    return {code for glyph in font for code in glyph.unicodes}


def verticalForms(fontName: str) -> set[str]:
    forms: set[str] = set()
    for glyph in Font.open(fontsDir / fontName):
        name = glyph.name
        if name and name.endswith(".vert"):
            forms.add(name)
    return forms


@pytest.mark.parametrize(("fontName", "locales"), sorted(FONTS.items()))
def test_nonJoining(fontName: str, locales: list[LocaleID]) -> None:
    drawn = codePoints(fontName)
    for locale in locales:
        given = data.nonJoining[locale]
        missing = {*given.punctuation, *given.digits} - drawn
        assert not missing, (
            f"{fontName} draws none of {[hex(i) for i in sorted(missing)]}, which {locale} writes"
        )


@pytest.mark.parametrize("fontName", ALL_FONTS)
def test_verticalForms(fontName: str) -> None:
    """A mark drawn with a vertical form has one wherever the mark is drawn.

    A vertical form is drawn for the mark itself rather than for a writing system, so the
    fonts do not differ on which marks have one: a mark the unified font draws a vertical
    form for is written with that form wherever the mark is written. A template writes its
    `vert` feature from the forms its font draws, and a form missing beside a mark is a mark
    that would stay upright in the column.
    """

    drawn = codePoints(fontName)
    reference = verticalForms("unified.ufo")
    expected = {f"u{code:04X}.vert" for code in drawn if f"u{code:04X}.vert" in reference}
    assert verticalForms(fontName) == expected
