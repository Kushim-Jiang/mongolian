import json
from importlib.resources import files
from typing import Any, Literal, TypeVar

from cattrs import structure

from .logic import resolveCmapVariants, resolveOutsideUnits
from .types import (
    FVS,
    AliasData,
    CharacterName,
    JoiningPosition,
    LocaleData,
    LocaleID,
    NonJoiningData,
    OutsideLetterData,
    ParticleData,
    VariantData,
    WrittenUnitID,
)

assert __package__
_dataDir = files(__package__)

_T = TypeVar("_T")


def _read(name: str) -> Any:
    """The JSON document *name* of the data directory."""

    with (_dataDir / name).open(encoding="utf-8") as f:
        return json.load(f)


def _model(name: str, model: type[_T]) -> _T:
    """The JSON document *name*, structured as *model*."""

    return structure(_read(name), model)


# The drawing of each written unit at each joining position: the code it is drawn with,
# and the codes of the shapes it takes in a context of its own, such as `pre_mvs`.
writtenUnits: dict[WrittenUnitID, dict[JoiningPosition, dict[str, int]]] = _read(
    "writtenUnits.json"
)

ligatures: dict[Literal["required", "optional"], dict[str, list[JoiningPosition]]] = _read(
    "ligatures.json"
)

locales = _model("locales.json", dict[LocaleID, LocaleData])
aliases = _model("aliases.json", dict[CharacterName, AliasData])
variants = _model(
    "variants.json", dict[CharacterName, dict[JoiningPosition, dict[FVS, VariantData]]]
)
particles = _model("particles.json", dict[LocaleID, dict[str, ParticleData]])
outsideLetters = _model(
    "outsideLetters.json",
    dict[CharacterName, dict[JoiningPosition, dict[FVS, OutsideLetterData]]],
)
nonJoining = _model("nonJoining.json", dict[LocaleID, NonJoiningData])

codePointToCmapVariant = resolveCmapVariants(variants)
codePointToOutsideUnits = resolveOutsideUnits(outsideLetters)
