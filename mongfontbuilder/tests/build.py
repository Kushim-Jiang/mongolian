"""Build the fonts this project composes, without running the suites.

    uv run python tests/build.py                  # every font
    uv run python tests/build.py --only unified   # only temp/unified.{ufo,otf}
    uv run python tests/build.py --only hudum     # only temp/hudum.{ufo,otf}

The suites compose the same fonts on the way to shaping them, which is a run of thousands of
cases: this builds them and stops. Nothing here shapes anything, so a change to a drawing or
to a layout of the font is built rather than checked — no case of the suites writes
punctuation, so for one, the conformance run says nothing about the vertical forms of the
marks.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from fixtures import buildFontForLocales
from mongfontbuilder import data
from mongfontbuilder.data.types import LocaleID
from unified import buildUnifiedFont
from utils import tempDir

# The writing systems whose font is built on its own: a writing system and its Ali Gali
# extension share a font, so the base writing system names it.
SINGLE_SYSTEM_LOCALES: tuple[LocaleID, ...] = ("MNG", "SIB", "MCH")

# The fonts that write with one writing system, by the name of the font. The unified font
# writes with every writing system at once and is composed by `unified.py`.
LOCALES: dict[str, list[LocaleID]] = {
    data.locales[locale].name: [locale] for locale in SINGLE_SYSTEM_LOCALES
}

# The fonts this builds, and the order they are built in.
NAMES = ["unified", *LOCALES]


def build(name: str) -> Path:
    """Build the font *name* and answer its path.

    Every font but the unified one has what is in ``temp/`` taken out of the way first, so
    that the build is a real one; the unified font is the one `buildUnifiedFont` builds,
    and that answers with the font it finds while the sources it is made of are unchanged.
    """

    if name == "unified":
        return buildUnifiedFont()

    # `buildFontForLocales` answers with the font it finds rather than composing it again,
    # and this is the build of the font, so what is there is taken out of the way first.
    for path in (tempDir / f"{name}.otf", tempDir / f"{name}.ufo"):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()

    return buildFontForLocales(LOCALES[name])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the fonts the suites would compose.")
    parser.add_argument(
        "--only",
        choices=[*NAMES, "all"],
        default="all",
        help="the font to build (default: every font)",
    )
    args = parser.parse_args()

    for name in NAMES if args.only == "all" else [args.only]:
        build(name)


if __name__ == "__main__":
    main()
