# Contributing Guide

## Contributing to the Python Package

The package is the project in [mongfontbuilder/](mongfontbuilder); its own README describes the library, the CLI, and the test suite. Set up the development environment using [uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
cd mongfontbuilder
uv sync
```

Write tests to verify your changes, then run them (from the project directory):

```sh
uv run pytest
```

Unfinished tasks or ideas can be added as [issues](https://github.com/Kushim-Jiang/mongolian/issues).

## Contributing to the Data Files

The source-of-truth data files are maintained as TypeScript files in [data/](data/). They are exported to JSON in [mongfontbuilder/src/mongfontbuilder/data/](mongfontbuilder/src/mongfontbuilder/data) for consumption of the Python API.

After editing any file in [data/](data/), re-run the export so the JSON stays in sync:

```sh
node data/export.ts
```

The export also validates the data (e.g. unique default variants, locale-specific aliases, GB/T 25914-2023 glyph-name format) and throws on any inconsistency.

## Contributing to the Templates

The [Glyphs](https://glyphsapp.com/) templates in [templates/](templates) are generated from the test UFO fonts and the OTL composer output. After changing the data files or the OTL rules, regenerate them:

```sh
uv run --directory mongfontbuilder python ../templates/update.py
```

This rewrites `hudum.glyphs`/`hudum.fea` and `manchu.glyphs`/`manchu.fea`. Template generation is **macOS-only** (it requires the Glyphs app via `glyphsLib`), and the corresponding tests in [`mongfontbuilder/tests/test_templates.py`](mongfontbuilder/tests/test_templates.py) are skipped on other platforms.

## Contributing to the Documentation

[![Built with Starlight](https://astro.badg.es/v2/built-with-starlight/tiny.svg)](https://starlight.astro.build)

The documentation site is the repository root itself. Install the Node dependencies:

```sh
npm install
```

Start a local development server:

```sh
npm run dev
```

Type-check the documentation before committing:

```sh
npm run check
```

Starlight looks for `.md` or `.mdx` files in the [docs/](docs/) directory. Each file is exposed as a route based on its file name. The `.mdx` files can include Svelte code, and standalone functions can be maintained as reusable components.

Reusable Svelte components that render the data tables (e.g. `LetterTable`, `ParticleTable`, `WrittenUnitTable`) live in [lib/](lib/). They read directly from the TypeScript data files in [data/](data/), so they stay in sync with the exported JSON automatically.

Images can be added to [src/](src/) and embedded in Markdown using relative links. And static assets, such as favicons, can be placed in [public/](public/).

## Checking Both Projects

Each project is checked by the tooling it carries, and the [`.vscode/`](.vscode) settings have the editors report the problems of the whole workspace rather than of the files that happen to be open:

- the Python package: ruff and pyright, both configured in [`mongfontbuilder/pyproject.toml`](mongfontbuilder/pyproject.toml);
- the documentation site: `npm run check` (`astro check`) for the TypeScript and `.astro` files, and `svelte-check` for the components.
