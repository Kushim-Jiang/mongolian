from pathlib import Path

import pytest
from fixtures import buildFontForLocales


@pytest.fixture(scope="session")
def hudum_font() -> Path:
    return buildFontForLocales(["MNG"])


@pytest.fixture(scope="session")
def manchu_font() -> Path:
    return buildFontForLocales(["MCH"])


@pytest.fixture(scope="session")
def sibe_font() -> Path:
    return buildFontForLocales(["SIB"])
