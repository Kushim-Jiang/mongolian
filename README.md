# Encoding and Shaping of the Mongolian Script

This repository maintains the documentation and the data files behind [UTN \#57, Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/) (the **Mongolian UTN**), the `mongfontbuilder` Python library that implements them, the font templates generated from that library, and the tests that validate the result.

The documentation is published at [mongolian.kushim.workers.dev](https://mongolian.kushim.workers.dev/).

The documentation site is the repository root itself; the parts it documents sit around it in directories of their own, each of the larger ones with a README:

| Part | What it is |
| --- | --- |
| [`data/`](data/README.md) | the specification data (TypeScript, the single source of truth) |
| [`mongfontbuilder/`](mongfontbuilder/README.md) | the Python project: the library, its CLI, and the tests |
| [`templates/`](templates/README.md) | the Glyphs templates and the script that updates them |

The root [`pyproject.toml`](pyproject.toml) declares the [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) that gives the Python one environment and one lockfile.

## Documentation site

The documentation is an [Astro](https://astro.build/) site built with [Starlight](https://starlight.astro.build/), and it is the repository root itself: its pages are the `.mdx` files in [`docs/`](docs/), its Svelte components and styles are in [`src/`](src/), its static assets are in [`public/`](public/), and its configuration and sidebar are [`astro.config.ts`](astro.config.ts). The site imports the data in [`data/`](data/README.md) directly, so the tables it renders stay in sync with the exported JSON.

Install the Node dependencies and start a local development server with:

```sh
npm install
npm run dev
```

The site is served at `http://localhost:4321`; [`CONTRIBUTING.md`](CONTRIBUTING.md) covers the other npm scripts and the contribution workflow.

## Continuous integration and publishing

The repository uses GitHub Actions:

- [`.github/workflows/test.yml`](.github/workflows/test.yml) syncs the workspace and runs the test suite of the package on pushes to `main`;
- [`.github/workflows/pypi.yml`](.github/workflows/pypi.yml) builds the package and publishes it to PyPI when a release is published;
- [`.github/workflows/pdf.yml`](.github/workflows/pdf.yml) builds the site and renders the documentation PDF, which it uploads as a workflow artifact; it runs only when dispatched by hand, not on pushes.

## Contributing

[`CONTRIBUTING.md`](CONTRIBUTING.md) covers the development environment of each part of the repository.
