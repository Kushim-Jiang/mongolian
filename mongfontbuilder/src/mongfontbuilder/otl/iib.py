from collections.abc import Iterator
from dataclasses import replace
from itertools import product
from typing import Literal

from fontTools import unicodedata

from .. import GlyphDescriptor, data, ligateParts, splitWrittens, writtenCombinations
from ..data.logic import choosesVariant
from ..data.types import JoiningPosition, LocaleID
from ..spec import GlyphSpec
from ..utils import getVariants, namespaceFromLocale
from . import MongFeaComposer, preMvsSuffixes

# The writing systems that draw the final form of the letter _m_ with a large tail, and the
# written units the localized treatment swaps: the form this font draws the character with,
# and the form the writing systems write instead.
LARGE_TAIL = ["SIB", "MCH"]
LOCALIZED_M_FINA = ("u182E.M.fina", "u182E.M3.fina")


def compose(c: MongFeaComposer) -> None:
    iib1(c)
    iib2(c)
    iib3(c)
    iib4(c)
    iib5(c)


def constructBowedForms(c: MongFeaComposer) -> None:
    """Draw the Hudum Ali Gali written forms that a bowed written unit is written with.

    A bowed written unit of Hudum Ali Gali that the word joins on the bow is written as one
    form: the `‹C›WpA` of the bow with the `Wp` and the `_a_` in the shape it takes after a
    `Wp`, and the `‹C›I4` of the bow with the Ali Gali _i_ that ends the word.
    """

    # The bowed written units of Hudum Ali Gali, which take a `Wp` and an `_a_`, or an _i_.
    BOWED_CONSONANTS = ["G", "K", "K2", "Bg", "Pg", "B"]

    # The written form of a bowed written unit that the word joins on the bow, the locale that
    # writes it, and the members it is drawn from — the bow at the joining position before the
    # one the written form is written in, where a `Wp`/`_a_` that follows makes it a ligature.
    BOWED_FORMS = {
        "WpA": (
            "MCHx",
            [("isol", "init"), ("fina", "medi")],
            lambda x, b: [f"_{x}O.{b}", "_A.fina.Wp_"],
        ),
        "I4": ("MNGx", [("isol", "init"), ("fina", "medi")], lambda x, b: [f"_{x}I.{b}"]),
    }

    for name, (locale, positions, members) in BOWED_FORMS.items():
        if locale not in c.locales:
            continue
        for position, base in positions:
            for consonant in BOWED_CONSONANTS:
                written = members(consonant, base)
                if all(i in c.glyphs for i in written):
                    c.spec.newGlyphs[f"_{consonant}{name}.{position}"] = GlyphSpec(written)


class LigatureCollector:
    """The ligatures of the ligature table, in the order they have to be written.

    A ligature may be written with the written form that a shorter ligature produces — the
    `‹C›WpA` of a bowed written unit with the `WpA` of the `Wp` and the `_a_` — so the
    written forms are taken from the shortest to the longest, and what a ligature produces
    is offered to the longer ones as an input. Inputs are deduplicated between writing
    systems, because they are written once for the font.
    """

    def __init__(self, c: MongFeaComposer) -> None:
        self.c = c
        self.substitutions = dict[tuple[GlyphDescriptor, ...], tuple[GlyphDescriptor, bool]]()
        self.writtenForms = dict[str, list[str]]()

    def collect(self) -> dict[tuple[GlyphDescriptor, ...], tuple[GlyphDescriptor, bool]]:
        for locale in self.c.locales:
            for category, ligatureToPositions in data.ligatures.items():
                self.collectCategory(locale, category, ligatureToPositions)
        return self.substitutions

    def collectCategory(
        self,
        locale: LocaleID,
        category: Literal["required", "optional"],
        ligatureToPositions: dict[str, list[JoiningPosition]],
    ) -> None:
        """Add the substitutions that the ligatures of one category have in *locale*.

        The written forms are taken from the shortest to the longest, because a longer
        written form may be written with what a shorter one produces.
        """

        for writtens, positions in sorted(
            ligatureToPositions.items(),
            key=lambda i: len(splitWrittens(i[0])),
        ):
            for position in positions:
                self.collectWrittenForm(locale, category, writtens, position)

    def collectWrittenForm(
        self,
        locale: LocaleID,
        category: str,
        writtens: str,
        position: JoiningPosition,
    ) -> None:
        """Add the substitutions that one written form has at one joining position."""

        required = category == "required"
        substitutions = iterLigatureSubstitutions(
            self.c, writtens, position, locale, self.writtenForms
        )
        for input, ligature in substitutions:
            if required and not isVowelFollower(locale, input):
                continue
            if existing := self.substitutions.get(input):
                assert existing == (ligature, required)
                continue
            self.substitutions[input] = ligature, required
            self.writtenForms[f"{''.join(ligature.units)}.{ligature.position}"] = [str(ligature)]


def isVowelFollower(locale: LocaleID, input: tuple[GlyphDescriptor, ...]) -> bool:
    """Whether the second glyph of *input* is a vowel, ignoring LVS.

    A glyph that is no character of its own — the written form that a shorter ligature
    produced — carries no alias of the writing system, and counts as one.
    """

    codePoint = input[1].codePoints[0]
    alias = data.aliases[unicodedata.name(chr(codePoint))]
    if isinstance(alias, dict):
        alias = alias.get(namespaceFromLocale(locale))
    return not isinstance(alias, str) or alias in data.locales[locale].categories["vowel"]


def iib1(c: MongFeaComposer) -> None:
    """
    **Phase IIb.1: Variation involving bowed written units**

    Ligatures.
    """

    constructBowedForms(c)
    # A mark between the parts of a ligature does not keep the ligature from being formed:
    # the Baluda of `G Baluda O` is a mark, and the two letters around it are still the
    # written form the ligature is drawn for.
    with c.Lookup("IIb.ligature", feature="rclt", flags={"IgnoreMarks": True}):
        for input, (ligature, _) in LigatureCollector(c).collect().items():
            implementLigature(c, input, ligature)

        if "MNGx" in c.locales:
            c.sub("u18A6.Wp.medi", "u1820.A.fina", by="u18A6_u1820.WpA.fina")
            c.sub("u188A.NG.init", "u1820.Aa.fina", by="u188A_u1820.NGAa.isol")
            c.sub("u188A.NG.medi", "u1820.Aa.fina", by="u188A_u1820.NGAa.fina")


def iterLigatureSubstitutions(
    c: MongFeaComposer,
    writtens: str,
    position: JoiningPosition,
    locale: LocaleID,
    writtenForms: dict[str, list[str]],
) -> Iterator[tuple[tuple[GlyphDescriptor, ...], GlyphDescriptor]]:
    for combination in writtenCombinations(splitWrittens(writtens), position):
        if len(combination) != 2:
            continue
        writtenLists = [
            [
                GlyphDescriptor.parse(glyph.glyph)
                for glyph in c.writtens(
                    locale,
                    *units.split("."),  # type: ignore
                ).glyphs
            ]
            or [GlyphDescriptor.parse(i) for i in writtenForms.get(units, [])]
            for units in combination
        ]
        for parts in product(*writtenLists):
            try:
                ligature = ligateParts([*parts])
            except KeyError:
                # The positions of these parts do not join — two final forms, for
                # example — so they form no ligature.
                continue
            yield parts, ligature


def implementLigature(
    c: MongFeaComposer,
    input: tuple[GlyphDescriptor, ...],
    ligature: GlyphDescriptor,
) -> None:
    inputNames = [str(i) for i in input]
    ligatureName = str(ligature)
    if c.glyphs and ligatureName not in c.glyphs:
        componentName = str(GlyphDescriptor([], ligature.units, ligature.position))
        if componentName not in c.glyphs and componentName not in c.spec.newGlyphs:
            # we don't check ligatures when generating, only generate OTL for existing glyphs,
            # so it's possible for the component to be missing.
            return
        c.spec.newGlyphs[c.glyphNameProcessor(ligatureName)] = GlyphSpec(
            [c.glyphNameProcessor(componentName)]
        )
    c.sub(*inputNames, by=ligatureName)


def iib2(c: MongFeaComposer) -> None:
    """
    **Phase IIb.2: The shape a written form takes before the mark that ends a syllable**

    The data gives a written unit a drawing of its own for the end of a syllable that a mark
    separates — `N.fina` and `Hx.fina` carry a `pre_mvs` code — and a chachlag onset writes
    it: the letter stands before the mark that precedes a chachlag _a_ or _e_. The source font
    draws that shape under the `mvs` suffix, `_N.fina.mvs` beside `_N.fina`.

    The mark the letter stands before is the narrow MVS, which is the shape the mark takes in
    the context that writes the chachlag _a_ or _e_, `III.a_e.chachlag`: the same lookup
    narrows the mark and chooses the vowel. A wide MVS is the separator that the cleanup of
    phase IIb.3 splits in two, and it is not a context for this form.

    The form is replaced here rather than by the condition that selects it, because the form
    that condition selects is the one the FVS has already chosen: a substitution made before
    the FVS is shaped would take the form out of the class the FVS is shaped against, and the
    FVS would be left in the text unshaped.
    """

    if not {"MNG", "MNGx"}.intersection(c.locales):
        return

    substitutions: list[tuple[str, str]] = []
    # The letters the chachlag onset of III.2c narrows the mark after, which are the ones a
    # mark can follow at the end of a syllable; of them, only the ones drawn with a `pre_mvs`
    # shape of their own take the form.
    for _, charName, position, _, variant in getVariants("MNG", ["n", "j", "w", "h", "g"]):
        if not choosesVariant("MNG", variant, "chachlag_onset"):
            continue
        form = GlyphDescriptor.fromData(charName, position, variant, locale="MNG")
        if not (suffixes := preMvsSuffixes(form)):
            continue
        written = str(form)
        mvs = str(replace(form, suffixes=suffixes))
        drawn = str(replace(form, codePoints=[], suffixes=suffixes))
        if not hasGlyph(c, written) or not hasGlyph(c, drawn):
            continue
        glyphSpec = GlyphSpec([c.glyphNameProcessor(drawn)])
        if pseudoPosition := form.pseudoPosition():
            glyphSpec.initPadding = pseudoPosition in ["isol", "init"]
            glyphSpec.finaPadding = pseudoPosition in ["isol", "fina"]
        c.spec.newGlyphs[c.glyphNameProcessor(mvs)] = glyphSpec
        substitutions.append((written, mvs))

    if not substitutions:
        return

    with c.Lookup("IIb.chachlag_onset.mvs.sub") as application:
        for written, mvs in substitutions:
            c.sub(written, by=mvs)

    with c.Lookup("IIb.chachlag_onset.mvs", feature="rclt", flags={"IgnoreMarks": True}):
        c.sub(
            c.input(c.glyphClass([i for i, _ in substitutions]), application),
            "mvs.narrow",
            c.glyphClass(["u1820.Aa.isol", "u1821.Aa.isol"]),
            by=None,
        )


def iib3(c: MongFeaComposer) -> None:
    """
    **Phase IIb.3: Cleanup of format controls**

    A wide MVS renders as a plain space-like separator. At this final stage it is
    split into a non-breaking space followed by an ignored zero-width MVS. The
    `nbspace` and `mvs.ignored` glyphs themselves are created up front in
    `initControls`; only the split substitution happens here.

    - `nbspace` -- identical to `space`, carrying NO-BREAK SPACE U+00A0. Using a
      non-breaking space here keeps the MVS separator from allowing a line break,
      just as the space set before a punctuation mark.
    - `mvs.ignored` -- an ignored, zero-width glyph that preserves the MVS.

    The pair `nbspace` + `mvs.ignored` therefore takes the place of `mvs.wide`.
    """

    with c.Lookup("IIb.cleanup.mvs.wide", feature="rclt"):
        c.sub("mvs.wide", by=["nbspace", "mvs.ignored"])


def iib4(c: MongFeaComposer) -> None:
    """
    **Phase IIb.4: Localized treatments**

    A character that the writing systems share may be written with a different design by
    each of them — the final form of the letter _m_ ends in a small tail in Hudum and in a
    large tail in Sibe and Manchu — and the font keeps one design as the default and gives
    the others theirs here.

    The localized form runs in `rclt` rather than in `locl`: an engine applies `locl` before
    cursive joining, when the character is still its bare glyph, so the written unit to
    replace does not exist yet.

    A font that writes with one of the writing systems alone already draws the design that
    writing system uses, so there is no design of another to localize: the written unit to
    replace is not drawn, and neither is the one to replace it with. The treatment is
    therefore written only where both are drawn, which is the font that writes with several
    writing systems at once.
    """

    if not (languages := [i for i in LARGE_TAIL if i in c.locales]):
        return
    if not all(hasGlyph(c, i) for i in LOCALIZED_M_FINA):
        return
    # The language system of a writing system is named after it, padded to four characters,
    # as the OpenType script/language tags are.
    tags = {i for i in c.languageSystems["mong"] if i.strip() in languages}
    with c.Lookup("IIb.localized.M.fina", feature="rclt", languageSystems={"mong": tags}):
        c.sub(LOCALIZED_M_FINA[0], by=LOCALIZED_M_FINA[1])


def hasGlyph(c: MongFeaComposer, name: str) -> bool:
    """Whether the composed font draws *name*, from the source font or from the spec.

    The source font is what the composition starts from and the spec is what it adds, so a
    glyph is drawn when either of them carries it. A phase that acts on a glyph the font
    does not draw has nothing to act on, and writing the rule anyway leaves the feature file
    referring to a glyph that is nowhere, which feaLib refuses.
    """

    return name in c.glyphs or name in c.spec.newGlyphs


def iib5(c: MongFeaComposer) -> None:
    """
    **Phase IIb.5: Optional treatments**

    Optional treatments.
    """
    pass
