from importlib.resources import files
from sys import version_info


testSuitesDir = files(__package__) if version_info < (3, 12) else files()  # type: ignore
"""The directory the suites are read from."""

glyphNameMapping: dict[str, str | None] = {
    # Whitespaces:
    "space": "space.Widespace.nomi",
    "nbspace": "nbspace.Widespace.nomi",
    # Spacing marks:
    "u1880": "u1880.Anusvara.nomi",
    "u1882": "u1882.Damaru.nomi",
    "u1883": "u1883.Ubadama.nomi",
    "u1884": "u1884.Invubadama.nomi",
    # Nonspacing marks:
    "u1885": "u1885.Baluda.mark",
    "u1886": "u1886.Tribaluda.mark",
    # Format controls:
    "fvs1": "u180B.Fvs1.nomi",
    "fvs2": "u180C.Fvs2.nomi",
    "fvs3": "u180D.Fvs3.nomi",
    "fvs4": "u180F.Fvs4.nomi",
    "mvs": "u180E.Mvs.nomi",
    "mvs.narrow": "u180E.Narrowspace.nomi",
    "nirugu": "u180A.Nirugu.medi",
    "nirugu.extend": None,
    "nnbsp": "u202F.Nnbsp.nomi",
}
"""Clarifies glyph names with their written unit info, for fonts built by this project."""
