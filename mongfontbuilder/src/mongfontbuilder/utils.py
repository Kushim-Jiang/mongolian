from collections.abc import Iterable, Iterator
from typing import cast, get_args

from . import data
from .data.types import FVS, CharacterName, JoiningPosition, LocaleID, LocaleNamespace, VariantData

namespaces: list[LocaleNamespace] = [*get_args(LocaleNamespace)]

charNameByNamespaceAlias: dict[tuple[LocaleNamespace, str], CharacterName] = {}
"""The character each alias names in each namespace.

`data.aliases` is read in the order it is written, so the character that answers an alias
first is the one the alias names. An alias written as a string is not specific to a
namespace, and names its character in every one of them.
"""

for _charName, _aliasData in data.aliases.items():
    _aliasPairs: list[tuple[LocaleNamespace, str]] = (
        [(_namespace, _aliasData) for _namespace in namespaces]
        if isinstance(_aliasData, str)
        else [*_aliasData.items()]
    )
    for _namespace, _alias in _aliasPairs:
        if _alias is not None:
            charNameByNamespaceAlias.setdefault((_namespace, _alias), _charName)


def namespaceFromLocale(locale: LocaleID) -> LocaleNamespace:
    return cast(LocaleNamespace, locale.removesuffix("x"))


def getVariants(
    locale: LocaleID,
    aliases: Iterable[str] | None = None,
) -> Iterator[tuple[str, CharacterName, JoiningPosition, FVS, VariantData]]:
    """Every variant of every letter of *locale*, with the letter it belongs to.

    A variant is one written form of one letter in one joining position, selected by an
    FVS: the FVS0 variant is the one the letter is written with by default, and the others
    are written when the FVS in the text asks for them. A variant is only written where
    the writing system that the locale belongs to answers it, so a caller that means to
    write it checks `locale in variant.locales`.
    """

    for alias in getAliasesByLocale(locale) if aliases is None else aliases:
        charName = getCharNameByAlias(locale, alias)
        for position, fvsToVariant in data.variants[charName].items():
            for fvs, variant in fvsToVariant.items():
                yield alias, charName, position, fvs, variant


def getCharNameByAlias(locale: LocaleID, alias: str) -> CharacterName:
    if character := charNameByNamespaceAlias.get((namespaceFromLocale(locale), alias)):
        return character
    raise ValueError(f"no alias {alias} found in {locale}")


def getAliasesByLocale(locale: LocaleID) -> list[str]:
    categories = data.locales[locale].categories
    return categories["vowel"] + categories["consonant"]
