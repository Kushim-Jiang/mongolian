from mongfontbuilder.otl import MongFeaComposer

from utils import tempDir


def test_fea() -> None:
    """The composer writes the whole feature file of a locale, glyphs or not."""

    composer = MongFeaComposer(cmap={}, glyphs=[], locales=["MNG"])
    composer.compose()
    code = composer.asFeatureFile().asFea()
    for system in ("DFLT dflt", "mong dflt", "mong MNG"):
        assert f"languagesystem {system};" in code
    for lookup in ("_.ignored", "_.valid", "_.reset", "MNG:particle"):
        assert f"lookup {lookup} {{" in code
    for feature in ("isol", "init", "medi", "fina", "rclt"):
        assert f"feature {feature} {{" in code
    (tempDir / "otl.fea").write_text(code)
