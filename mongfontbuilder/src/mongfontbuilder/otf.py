"""Compiling a composed font to OpenType.

A glyph of a composed font is often built from several drawn written units, whose outlines
meet and cross — the stem a bowed letter leaves to the letter after it, the long vowel sign
drawn into the shape it follows — and a glyph whose contours cross is filled differently by
different renderers: the outlines may not be left overlapping. The compile step therefore
removes the overlaps, which leaves the ink as it is and makes the glyph the same in every
renderer.
"""

from typing import Any

from fontTools.ttLib import TTFont
from ufo2ft import OTFCompiler
from ufo2ft.constants import CFFOptimization
from ufoLib2 import Font

# How the compiler is asked to remove overlaps: a boolean operation over every glyph's
# contours, after the components have been decomposed. `pathops` is the backend that
# handles the quadratic curves the drawings use, and the one ufo2ft recommends.
OVERLAPS_BACKEND = "pathops"


def compileOTF(font: Font, *, featureWriters: Any = None, removeOverlaps: bool = True) -> TTFont:
    """Compile *font* to an OpenType font with CFF outlines, overlaps removed.

    *featureWriters* is passed on to the compiler when it is not None, which is what the
    command line interface does to have the font carry the features it was composed with.
    """

    options: dict[str, Any] = {
        "useProductionNames": False,
        "optimizeCFF": CFFOptimization.NONE,
    }
    if removeOverlaps:
        options["removeOverlaps"] = True
        options["overlapsBackend"] = OVERLAPS_BACKEND
    if featureWriters is not None:
        options["featureWriters"] = featureWriters
    return OTFCompiler(**options).compile(font)
