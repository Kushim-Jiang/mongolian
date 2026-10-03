import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import uharfbuzz
from fontTools import unicodedata
from fontTools.ttLib import TTFont

from mongfontbuilder.data import LocaleID, aliases
from mongfontbuilder.testSuites import glyphNameMapping, testSuitesDir
from mongfontbuilder.utils import namespaceFromLocale

testsDir = Path(__file__).parent
fontsDir = testsDir / "fonts"  # the test fonts the suites shape
project = testsDir.parent  # the mongfontbuilder project this suite belongs to
repo = project.parent  # the repository, where the templates live
tempDir = project / "temp"
tempDir.mkdir(exist_ok=True)


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

    def codePointAgnostic(self) -> str:
        return ".".join(i for i in ["".join(self.writtenUnits), self.joiningPosition] if i)


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
            charName = next(
                k
                for k, v in aliases.items()
                if (isinstance(v, dict) and v.get(namespaceFromLocale(locale)) == name)
                or v == name
            )
            result.append(unicodedata.lookup(charName))
        except StopIteration:
            raise ValueError(f"No alias found for name: {name}") from None

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


def makeFontFilename(font: TTFont) -> str:
    from fontTools.ttLib.tables._n_a_m_e import table__n_a_m_e

    table: table__n_a_m_e = font["name"]  # type: ignore
    postScriptName = table.getDebugName(6)
    assert postScriptName

    suffix = ".otf" if {"CFF ", "CFF2"}.intersection(font.keys()) else ".ttf"
    return postScriptName + suffix
