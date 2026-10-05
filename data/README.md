# Specification data

The canonical specification data of [UTN \#57, Encoding and Shaping of the Mongolian Script](https://www.unicode.org/notes/tn57/) (the **Mongolian UTN**), maintained as TypeScript files. They are the single source of truth for the characters, written units, variants, aliases, ligatures, and particles of every supported writing system.

The files correspond to the entities of the character layer described in the [Architecture](https://mongolian.kushim.workers.dev/architecture/) chapter of the documentation:

- [`locales.ts`](locales.ts) — the writing systems (MNG, TOD, SIB, MCH) together with their name, their shaping conditions and their categories of characters;
- [`writtenUnits.ts`](writtenUnits.ts) — the written units of the letters; the characters of the script that do not join, which are the punctuation marks, each with the writing systems that write it, and the Mongolian digits; and the format controls;
- [`variants.ts`](variants.ts) — the variants of each letter by cursive position and by FVS, including which variant is the default; this is where the FVS assignments of each writing system are defined;
- [`outsideLetters.ts`](outsideLetters.ts) — the letters that lie outside every writing system, keyed by character name, by cursive position and by FVS the way the variants of a character are, together with the written units that draw them;
- [`aliases.ts`](aliases.ts), [`ligatures.ts`](ligatures.ts), [`particles.ts`](particles.ts) — the aliases, ligatures, and particles used by the data;
- [`misc.ts`](misc.ts) — the character-name and joining-position types shared by the data;
- [`export.ts`](export.ts) — exports the JSON copies for the code library.

## Exporting the JSON

The documentation site imports these TypeScript files directly at build time to render the tables of the per-writing-system chapters. The Python library reads JSON copies of them, so a change to the model begins by editing the TypeScript sources and then regenerating the JSON. Run, from the repository root:

```sh
node data/export.ts
```

which writes `locales.json`, `aliases.json`, `writtenUnits.json`, `ligatures.json`, `variants.json`, `particles.json`, `outsideLetters.json`, and `nonJoining.json` into [`mongfontbuilder/src/mongfontbuilder/data/`](../mongfontbuilder/src/mongfontbuilder/data/). The last of them is the code points of the characters that do not join, by writing system, which is what a font of that writing system has to draw.

The export step also validates the data: every variant set must have exactly one default, the conditions and categories of each writing system must be consistent with the variant data, and the national-standard references must match their expected format. The JSON files are generated: edit the TypeScript sources and rerun the export; do not edit the JSON files by hand.

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the contribution workflow.
