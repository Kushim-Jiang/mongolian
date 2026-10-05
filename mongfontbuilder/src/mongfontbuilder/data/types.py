from dataclasses import dataclass, field
from typing import Literal, NamedTuple, get_args

from cattrs import register_structure_hook

JoiningPosition = Literal["isol", "init", "medi", "fina"]
joiningPositions: list[JoiningPosition] = [*get_args(JoiningPosition)]
isol, init, medi, fina = joiningPositions

WrittenUnitID = str
LocaleID = Literal["MNG", "MNGx", "TOD", "TODx", "SIB", "MCH", "MCHx"]
Condition = str
CharacterName = str
FVS = int

LocaleNamespace = Literal["MNG", "TOD", "SIB", "MCH"]
AliasData = str | dict[LocaleNamespace, str]
register_structure_hook(AliasData, lambda x, _: x)


@dataclass
class LocaleData:
    name: str
    conditions: list[Condition]
    categories: dict[str, list[str]]


class VariantReference(NamedTuple):
    position: JoiningPosition
    fvs: FVS
    locale: LocaleID | None = None


@dataclass
class ParticleData:
    form: str
    indices: list[int]


Written = list[WrittenUnitID] | VariantReference


def _structureWritten(x, _):
    return VariantReference(*x) if x[0] in joiningPositions else x


register_structure_hook(Written, _structureWritten)
register_structure_hook(Written | None, lambda x, _: _structureWritten(x, None) if x else None)


@dataclass
class VariantLocaleData:
    written: Written | None = None
    conditions: list[Condition] = field(default_factory=list)
    archaic: bool = False
    gb: str = ""
    eac: str = ""
    lvs: bool = False


@dataclass
class VariantData:
    written: Written
    default: bool = False
    locales: dict[LocaleID, VariantLocaleData] = field(default_factory=dict)


@dataclass
class NonJoiningData:
    """The characters of a writing system that are not letters and take no part in shaping.

    They are the code points a font of the writing system has to carry: the punctuation
    marks the writing system writes, and the digits it writes numbers with, where it has
    digits of its own.
    """

    punctuation: list[int]
    digits: list[int]


@dataclass
class OutsideLetterData:
    written: Written
