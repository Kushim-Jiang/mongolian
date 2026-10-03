glyphNameMapping: dict[str, str | None] = {
    # Whitespaces:
    "space": "uni0020.Widespace.nomi",
    "uni0020": "uni0020.Widespace.nomi",
    "nbspace": "nbspace.Widespace.nomi",
    # Digits:
    "uni1810": "uni1810.Zero.nomi",
    "uni1811": "uni1811.One.nomi",
    "uni1812": "uni1812.Two.nomi",
    "uni1813": "uni1813.Three.nomi",
    "uni1814": "uni1814.Four.nomi",
    "uni1815": "uni1815.Five.nomi",
    "uni1816": "uni1816.Six.nomi",
    "uni1817": "uni1817.Seven.nomi",
    "uni1818": "uni1818.Eight.nomi",
    "uni1819": "uni1819.Nine.nomi",
    # Spacing marks:
    "uni1880": "uni1880.Anusvara.nomi",
    "uni1880.fvs1": "uni1880.Anusvara2.nomi",
    "uni1881": "uni1881.Visarga.nomi",
    "uni1881.fvs1": "uni1881.Visarga2.nomi",
    "uni1882": "uni1882.Damaru.nomi",
    "uni1883": "uni1883.Ubadama.nomi",
    "uni1884": "uni1884.Invubadama.nomi",
    # Nonspacing marks:
    "baluda": "uni1885.Baluda.mark",
    "tribaluda": "uni1886.Tribaluda.mark",
    "dagalga": "uni18A9.Dagalga.mark",
    # Format controls:
    "fvs1": "uni180B.Fvs1.nomi",
    "fvs2": "uni180C.Fvs2.nomi",
    "fvs3": "uni180D.Fvs3.nomi",
    "fvs4": "uni180F.Fvs4.nomi",
    "lvs.ignored": "uni1843.Lv.mark",
    "mvs": "uni180E.Mvs.nomi",
    "mvs.narrow": "uni180E.Narrowspace.nomi",
    "mvs.wide": "uni180E.Widespace.nomi",
    "nirugu": "uni180A.Nirugu.medi",
    "nirugu.extend": None,
    "nnbsp": "uni202F.Nnbsp.nomi",
    "zwj": "uni200D.Zwj.nomi",
    "zwnj": "uni200C.Zwnj.nomi",
}
"""Clarifies glyph names with their written unit info, for fonts built by this project."""
