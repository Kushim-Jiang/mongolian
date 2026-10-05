import re
from collections.abc import Callable
from functools import cache
from hashlib import sha256
from os import environ
from pathlib import Path
from typing import TypeVar

import uharfbuzz
from fontTools import unicodedata
from ufoLib2 import Font

from mongfontbuilder.data import LocaleID, aliases
from mongfontbuilder.otl import MongFeaComposer
from mongfontbuilder.spec import applySpecToFont
from mongfontbuilder.testSuites import glyphNameMapping
from mongfontbuilder.testSuites import testSuitesDir as testSuitesDir  # re-exported for fixtures
from mongfontbuilder.utils import getCharNameByAlias, namespaceFromLocale

testsDir = Path(__file__).parent
fontsDir = testsDir / "fonts"  # the test fonts the suites shape
project = testsDir.parent  # the mongfontbuilder project this suite belongs to
repo = project.parent  # the repository, where the templates live
tempDir = project / "temp"  # the builds and reports the tests write
tempDir.mkdir(exist_ok=True)  # made here, and imported ready-made by every other module
libraryDir = project / "src" / "mongfontbuilder"  # the code and the data a font is composed from

Composer = TypeVar("Composer", bound=MongFeaComposer)


def sourceStamp(*paths: Path, extra: str = "") -> str:
    """A digest of everything a built test font is made of.

    A build is reused while its sources are the same, and is repeated when any of them
    changes. The digest is taken of the file contents rather than of their timestamps, so
    a build is not reused after a file is put back to an earlier state either. *paths* are
    read whole when they are files, and walked when they are directories; *extra* is
    anything else the build depends on, such as the writing systems it targets.
    """

    digest = sha256(extra.encode())
    for path in sorted(paths, key=lambda i: i.as_posix()):
        digest.update(path.as_posix().encode())
        files = sorted(path.rglob("*"), key=lambda i: i.as_posix()) if path.is_dir() else [path]
        for file in files:
            # The bytecode Python writes beside the sources is not part of a build, and
            # walking it would make the digest depend on which interpreters have run.
            if file.is_file() and "__pycache__" not in file.parts:
                digest.update(file.relative_to(path).as_posix().encode() if path.is_dir() else b"")
                digest.update(file.read_bytes())
    return digest.hexdigest()


def cachedBuild(stamp: str, artifacts: list[Path], stampFile: Path) -> bool:
    """Whether *artifacts* are still the build *stamp* describes.

    `MONGFONTBUILDER_REBUILD` in the environment asks for every build to be repeated, which
    is what a run that means to test the composition itself sets.
    """

    if environ.get("MONGFONTBUILDER_REBUILD"):
        return False
    return (
        all(i.exists() for i in artifacts)
        and stampFile.is_file()
        and stampFile.read_text(encoding="utf-8") == stamp
    )


def recordBuild(stamp: str, stampFile: Path) -> None:
    """Record that the artifacts just written are the build *stamp* describes."""

    stampFile.write_text(stamp, encoding="utf-8")


class UTNGlyphName(str):
    """
    Besides the graphical .joining_position, there’s also a joining position in terms of shaping logic that may appear in a glyph name. For example, uni1828.N.init@isol — a glyph name written uni1828.N.init._isol, as `parseWrittenUnits` rewrites it — is an isol glyph in terms of shaping, but graphically it’s actually N.init.
    """

    uniName: str | None
    writtenUnits: list[str]
    joiningPosition: str | None  # isol | init | medi | fina

    def __init__(self, name: str) -> None:
        parts = name.split(".")
        if len(parts) == 1:
            self.uniName, self.writtenUnits, self.joiningPosition = parts[0], [], None
            return

        if len(parts) == 3:
            self.uniName = parts[0]
            written_units_part, self.joiningPosition = parts[1:]
        else:  # 2
            self.uniName = None
            written_units_part, self.joiningPosition = parts
        self.writtenUnits = re.findall("[A-Z][a-z0-9]*", written_units_part)


def getWrittenUnits(utnName: UTNGlyphName) -> str:
    position = utnName.joiningPosition or ""
    units: list[str]
    if position.startswith("init"):
        units = [*utnName.writtenUnits, "Right"]
    elif position.startswith("medi"):
        units = ["Left", *utnName.writtenUnits, "Right"]
    elif position.startswith("fina"):
        units = ["Left", *utnName.writtenUnits]
    else:
        units = utnName.writtenUnits
    return "".join(units)


def parseAliases(text: str, locale: LocaleID) -> str:
    result = []
    for char in text:
        alias = aliases[unicodedata.name(char)]
        if isinstance(alias, str):
            result.append(alias)
        else:
            result.append(alias[namespaceFromLocale(locale)])

    return " ".join(result)


def parseLetter(names: str, locale: LocaleID) -> str:
    result = []

    for name in names.split():
        try:
            charName = getCharNameByAlias(locale, name)
        except ValueError:
            raise ValueError(f"No alias found for name: {name}") from None
        result.append(unicodedata.lookup(charName))

    return "".join(result)


@cache
def loadHBFont(path: Path) -> uharfbuzz.Font:  # type: ignore
    from uharfbuzz import Blob, Face, Font  # type: ignore

    return Font(Face(Blob.from_file_path(path)))


def parseWrittenUnits(text: str, font: Path, language: str | None = None) -> str:
    from uharfbuzz import Buffer, shape  # type: ignore

    hbFont = loadHBFont(font)
    buffer = Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    if language:
        buffer.language = language
    shape(hbFont, buffer)

    glyphNames = [hbFont.glyph_to_string(info.codepoint) for info in buffer.glyph_infos]
    writtenUnits = ""

    for glyphName in glyphNames:
        name = glyphNameMapping.get(glyphName) or glyphName
        utnName = UTNGlyphName(name.replace("._", "@").replace(".mvs", "@mvs"))
        writtenUnits += getWrittenUnits(utnName)

    writtenUnits = (
        writtenUnits.replace("RightLeft", "")
        .replace("RightBaludaLeft", "Baluda")
        .replace("RightTribaludaLeft", "Tribaluda")
    )
    return (
        " ".join(UTNGlyphName(f".{writtenUnits}.").writtenUnits)
        .replace("Nirugu", "Ni")
        .replace("Left", "<")
        .replace("Right", ">")
        .replace("Widespace", "-")
        .replace("Narrowspace", "_")
    )


def composeInto(
    font: Font,
    locales: list[LocaleID],
    composerClass: type[Composer] = MongFeaComposer,
) -> Composer:
    """Compose *font* with *composerClass*, apply the spec to it, and answer the composer.

    The composer is built from the code points and the glyphs *font* carries, so every
    builder of the suites reaches the composition the same way.
    """

    composer = composerClass(
        cmap={j: i for i in font.keys() for j in font[i].unicodes},
        glyphs=[*font.keys()],
        locales=locales,
    )
    applySpecToFont(composer.compose(), font)
    return composer


def assertWrittenUnits(
    index: str,
    letters: str,
    locale: LocaleID,
    goal: str,
    font: Path,
    language: str | None = None,
    report: Callable[[str, str], None] | None = None,
) -> None:
    """Shape one case of a suite against *font*, and assert the written units it answers.

    *letters* is the case as the suite writes it, in aliases; *goal* is the written units
    the suite expects, as `getWrittenUnits` reads them off a shape. *language* is the
    language of the writing system, which a font that answers for several of them is shaped
    with; *report* is told the index and the answer before the assertion, for a run that
    prints where it has come.
    """

    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, font, language)
    if report:
        report(index, "ok" if result == goal else "failed")
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"
