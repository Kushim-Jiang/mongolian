import re
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from os import environ
from pathlib import Path

import uharfbuzz
from fontTools import unicodedata

from mongfontbuilder.data import LocaleID, aliases
from mongfontbuilder.testSuites import glyphNameMapping, testSuitesDir
from mongfontbuilder.utils import getCharNameByAlias, namespaceFromLocale

testsDir = Path(__file__).parent
fontsDir = testsDir / "fonts"  # the test fonts the suites shape
project = testsDir.parent  # the mongfontbuilder project this suite belongs to
repo = project.parent  # the repository, where the templates live
tempDir = project / "temp"
tempDir.mkdir(exist_ok=True)
libraryDir = project / "src" / "mongfontbuilder"  # the code and the data a font is composed from


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
            if file.is_file():
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


@dataclass
class UTNGlyphName(str):
    """
    Besides the graphical .joining_position, there’s also a joining position in terms of shaping logic that may appear in a glyph name. For example, uni1828.N.init._isol is an isol glyph in terms of shaping, but graphically it’s actually N.init.
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

    def codePoint(self) -> int | None:
        if self.uniName:
            return int(self.uniName.removeprefix("uni"), 16)
        else:
            return None


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


def assertWrittenUnits(
    index: str,
    letters: str,
    locale: LocaleID,
    goal: str,
    font: Path,
) -> None:
    """Shape one case of a suite against *font*, and assert the written units it answers.

    *letters* is the case as the suite writes it, in aliases; *goal* is the written units
    the suite expects, as `getWrittenUnits` reads them off a shape.
    """

    parsedText = parseLetter(letters, locale)
    codes = parseAliases(parsedText, locale)
    result = parseWrittenUnits(parsedText, font)
    assert result == goal, f"ind:  {index}\ncode: {codes}\nres:  {result}\ngoal: {goal}"
