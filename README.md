# Encoding and Shaping of the Mongolian Script

This repository maintains the working draft of [UTN \#57, Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/) (the **Mongolian UTN**): the documentation and the data files behind it, the `mongfontbuilder` Python library that implements them, the font templates generated from that library, and the tests that validate the result.

The working draft is published continuously at [mongolian.kushim.workers.dev](https://mongolian.kushim.workers.dev/). Stable revisions are periodically published and archived by the Unicode Consortium as versions of the UTN; those archived versions are the official ones.

The documentation site is the repository root itself; the parts it documents sit around it in directories of their own:

```text
mongolian/
├─ data/                the specification data (TypeScript, the single source of truth)
├─ docs/                the documentation pages (.mdx)
├─ lib/                 the Svelte components (data tables, writing-system tags)
├─ public/              the static assets
├─ src/                 site styles and configuration
├─ templates/           the Glyphs templates and the script that updates them
├─ mongfontbuilder/     the Python project: the library, its CLI, and the tests
├─ astro.config.ts      documentation site configuration and sidebar
└─ check.py             the unified check entry point (ruff, pyright, astro, svelte)
```

This repository consists of:

- **Documentation and data files** that clarify the encoding and shaping rules required for a font to be compatible with the Unicode Standard and China’s national standard GB/T 25914-2023.
- **`mongfontbuilder`**, the Python library that helps font designers and developers produce a standard-compatible Mongolian script font, as clarified by the documentation.
  - It also acts as the reference implementation of the Mongolian UTN.
- **Templates** for generating fonts in Glyphs app from the library’s output.
- **Tests** for validating fonts produced by the library across multiple Mongolian writing systems (Hudum, Sibe, Manchu).

## Documentation and data files

The documentation is maintained in [docs/](https://github.com/Kushim-Jiang/mongolian/blob/main/docs) and deployed to [mongolian.kushim.workers.dev](https://mongolian.kushim.workers.dev/). For contribution guidelines, refer to [CONTRIBUTING.md](https://github.com/Kushim-Jiang/mongolian/blob/main/CONTRIBUTING.md).

The source-of-truth data files are maintained as TypeScript files in [data/](https://github.com/Kushim-Jiang/mongolian/blob/main/data). They’re exported to JSON in [mongfontbuilder/src/mongfontbuilder/data/](https://github.com/Kushim-Jiang/mongolian/tree/main/mongfontbuilder/src/mongfontbuilder/data) for consumption of the Python API.

## The `mongfontbuilder` library

The Python library `mongfontbuilder` is maintained in [mongfontbuilder/](https://github.com/Kushim-Jiang/mongolian/blob/main/mongfontbuilder) and published to [PyPI](https://pypi.org/project/mongfontbuilder/):

```sh
pip install mongfontbuilder
```

Its own README, [`mongfontbuilder/README.md`](mongfontbuilder/README.md), describes the Python API, the CLI, the development environment, and the test suite.

## Templates

Maintained in [templates/](https://github.com/Kushim-Jiang/mongolian/blob/main/templates).

`mongfontbuilder` can generate [Glyphs](https://glyphsapp.com/) templates (`.glyphs` files) from the UFO test fonts and the OTL composer output. These templates let type designers open and work with the generated glyph layout directly in Glyphs app.

The template update script is at [`templates/update.py`](https://github.com/Kushim-Jiang/mongolian/blob/main/templates/update.py). Currently available templates:

- `hudum.glyphs` — Hudum (MNG) template.
- `manchu.glyphs` — Manchu (MCH) template.

Template tests are macOS-only (require Glyphs app) and located in [`mongfontbuilder/tests/test_templates.py`](https://github.com/Kushim-Jiang/mongolian/blob/main/mongfontbuilder/tests/test_templates.py).

## Tests

Maintained in [mongfontbuilder/tests/](https://github.com/Kushim-Jiang/mongolian/blob/main/mongfontbuilder/tests), and run with `uv run pytest` from the `mongfontbuilder/` project.

The test harness builds each font on the fly using `mongfontbuilder`’s Python API directly, then shapes the test input strings with [HarfBuzz](https://harfbuzz.github.io/) and compares the resulting glyph sequence against expected output. Tests are organized per writing system with separate test fonts:

- **Hudum** (`MNG`): validated against the EAC and core test suites (`eac-hud`, `core-hud`).
- **Manchu** (`MCH`): validated against the core test suite (`core-man`).
- **Sibe** (`SIB`): validated against the core test suite (`core-sib`).

Where the UTN model answers a case of the EAC suite differently, the case is kept in the suite as an expected failure and its reason is written down; the cases are listed in [`mongfontbuilder/README.md`](mongfontbuilder/README.md).

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) covers the development environment of each part of the repository, and [`check.py`](check.py) at the root runs every checker of both projects:

```sh
uv run --no-project python check.py
```
