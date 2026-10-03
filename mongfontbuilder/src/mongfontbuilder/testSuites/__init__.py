from importlib.resources import files
from pathlib import Path


testSuitesDir = files(__package__) if __package__ else Path(__file__).parent
"""The directory the suites are read from."""

glyphNameMapping: dict[str, str | None] = {
    # Whitespaces:
    "space": "space.Widespace.nomi",
    "nbspace": "nbspace.Widespace.nomi",
    # Digits:
    "u1810": "u1810.Zero.nomi",
    "u1811": "u1811.One.nomi",
    "u1812": "u1812.Two.nomi",
    "u1813": "u1813.Three.nomi",
    "u1814": "u1814.Four.nomi",
    "u1815": "u1815.Five.nomi",
    "u1816": "u1816.Six.nomi",
    "u1817": "u1817.Seven.nomi",
    "u1818": "u1818.Eight.nomi",
    "u1819": "u1819.Nine.nomi",
    # Spacing marks:
    "u1880": "u1880.Anusvara.nomi",
    "u1880.fvs1": "u1880.Anusvara2.nomi",
    "u1881": "u1881.Visarga.nomi",
    "u1881.fvs1": "u1881.Visarga2.nomi",
    "u1882": "u1882.Damaru.nomi",
    "u1883": "u1883.Ubadama.nomi",
    "u1884": "u1884.Invubadama.nomi",
    # Nonspacing marks:
    "u1885": "u1885.Baluda.mark",
    "u1886": "u1886.Tribaluda.mark",
    "u18A9": "u18A9.Dagalga.mark",
    # Format controls:
    "fvs1": "u180B.Fvs1.nomi",
    "fvs2": "u180C.Fvs2.nomi",
    "fvs3": "u180D.Fvs3.nomi",
    "fvs4": "u180F.Fvs4.nomi",
    "lvs.ignored": "u1843.Lv.mark",
    "mvs": "u180E.Mvs.nomi",
    "mvs.narrow": "u180E.Narrowspace.nomi",
    "mvs.wide": "u180E.Widespace.nomi",
    "nirugu": "u180A.Nirugu.medi",
    "nirugu.extend": None,
    "nnbsp": "u202F.Nnbsp.nomi",
    "zwj": "u200D.Zwj.nomi",
    "zwnj": "u200C.Zwnj.nomi",
}
"""Clarifies glyph names with their written unit info, for fonts built by this project."""
