# mongfontbuilder

The Python library that helps font designers and developers produce a standard-compatible Mongolian script font, as clarified by the documentation of the working draft of [UTN \#57, Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/) (the **Mongolian UTN**). It also acts as the reference implementation of that document.

The library is maintained in this project and published to [PyPI](https://pypi.org/project/mongfontbuilder/). To install it in terminal:

```sh
pip install mongfontbuilder
```

The library includes various utilities, including:

- Python API for the data files.
- Dynamic generation of OpenType Layout rules.
- Construction of a complete font from a minimal glyph set.

A CLI is also available — it reads a source UFO font and writes a complete font with the generated OTL rules:

```sh
uv run python -m mongfontbuilder input.ufo output.otf --locales MNG
```

Both `.ufo` and `.otf` output formats are supported. See `--help` for available locales.

The documentation, the specification data, and the Glyphs templates are maintained in the repository this project belongs to, [Kushim-Jiang/mongolian](https://github.com/Kushim-Jiang/mongolian).

## Development

The project is developed with [uv](https://docs.astral.sh/uv/getting-started/installation/). The commands below are run from this project directory, `mongfontbuilder/`. Set up the environment and install the development tools (pytest, ruff, pyright, uharfbuzz, glyphsLib) with:

```sh
uv sync
```

## Tests

The test suite is run with:

```sh
uv run pytest
```

The harness builds each test font on the fly using the package API, shapes the test strings with [HarfBuzz](https://harfbuzz.github.io/), and compares the resulting glyph sequence with the expected output. The tests are organized per writing system, each with its own UFO test font and test cases under `tests/data/`:

- **Hudum** (`MNG`), from `tests/fonts/hudum.ufo`, is validated against the EAC and core suites (`eac-hud`, `core-hud`);
- **Manchu** (`MCH`), from `tests/fonts/manchu.ufo` and `tests/fonts/manchu-ag.ufo`, is validated against the core suite (`core-man`);
- **Sibe** (`SIB`), from `tests/fonts/sibe.ufo`, is validated against the core suite (`core-sib`).

A font that writes with every writing system at once, from `tests/fonts/unified.ufo`, is validated against the same cases by `tests/test_unified.py`; the font it composes and the cases it runs are in `tests/unified.py`.

### Cases the EAC expects differently

The EAC suite is settled by the Hudum standard alone. Where the UTN model disagrees with it, the case is marked as an expected failure — it is kept in the suite, and the reason is kept in [`tests/fixtures.py`](tests/fixtures.py) — so that the run stays green and the disagreement stays visible.

A font that writes with every writing system at once (`test_unified.py`) is the one that has to be marked for the cases below: the meeting held that the effect of an FVS does not depend on the locale, so the FVS stays valid and selects its variant wherever the character is shared. A font that writes with one writing system answers them as the EAC expects.

- `MND11-2`, `MNM10-2`, `MNM11-2`, `MNS11-26`, `MNZ11-3`, `MNZ21-5`, `XIM11-11`, `XIM11-675`, `XIM11-678`, `XIM11-681`, `XIM11-684`, `XIM11-687`, `XIM11-690`, `XIM11-694`

`XIM11-46` (`e n fvs3 mvs e`) is answered differently by every font as well, but for a reason of its own: the FVS3 follows the _n_, and the UTN model draws the form it selects rather than the one the EAC expects.

The cases below are marked for every font, because the UTN model answers them differently from the EAC in a way that does not depend on which writing systems a font carries.

- `XIM11-39`, `XIM11-40`, `XIM11-41` — the UTN model keeps the old functionality of NNBSP, so the features of NNBSP stay on.
- `XIM11-1012` — a letter before an MVS is in the final position, so the FVS after it selects the final variant.

## Glyphs templates

The [Glyphs](https://glyphsapp.com/) templates in the repository's [`templates/`](../templates) directory are generated from the test UFO fonts and the output of the OTL composer, and are updated from this project with:

```sh
uv run python ../templates/update.py
```

This rewrites `hudum.glyphs`/`hudum.fea` and `manchu.glyphs`/`manchu.fea`. Template generation is **macOS-only** (it requires the Glyphs app via `glyphsLib`), and the corresponding tests in [`tests/test_templates.py`](tests/test_templates.py) are skipped on other platforms.
