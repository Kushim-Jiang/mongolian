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

from unified import (
    CASES,
    LANGUAGE,
    buildUnifiedFont,
    caseIndexes,
    composedUFO,
    languageOf,
)
from utils import parseAliases, parseLetter, parseWrittenUnits


@pytest.fixture(scope="session")
def unifiedFont() -> Path:
    """The unified font, composed once for the whole session.

    Composing the font and compiling it takes a while, so the whole session shares one
    build; the composed UFO and OTF are left in ``temp/``.
    """

    return buildUnifiedFont()


def test_unified(unifiedFont: Path) -> None:
    assert composedUFO.exists()
    assert unifiedFont.exists()


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
    locale: str,
    goal: str,
    unifiedFont: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, unifiedFont, languageOf(LANGUAGE[locale]))
    with capsys.disabled():
        report(index, "ok" if result == goal else "failed")
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"
