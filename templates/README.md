# Glyphs templates

The [Glyphs](https://glyphsapp.com/) templates generated from the test UFO fonts and the output of the OTL composer, together with the script that rebuilds them.

```text
templates/
├─ update.py       the template update script
├─ hudum.glyphs    the Hudum template
├─ hudum.fea       its OpenType Layout source
├─ manchu.glyphs   the Manchu template
└─ manchu.fea      its OpenType Layout source
```

Regenerate the templates from the repository root with:

```sh
uv run python templates/update.py
```

which rewrites `hudum.glyphs`/`hudum.fea` and `manchu.glyphs`/`manchu.fea` from [`mongfontbuilder/tests/fonts/hudum.ufo`](../mongfontbuilder/tests/fonts/hudum.ufo) and [`mongfontbuilder/tests/fonts/manchu.ufo`](../mongfontbuilder/tests/fonts/manchu.ufo). The templates let type designers open and work with the generated glyph layout in the Glyphs app.

A template carries the whole font: the letters the composition builds, the characters of the writing system that do not join — its marks, and its digits where it writes numbers with them ([`data/writtenUnits.ts`](../data/writtenUnits.ts)) — and a `vert` feature that writes each mark with its vertical form where the font draws one. Both files are written with `\n` whatever the platform, so a template generated on one machine is the template generated on another.

Generation needs only `glyphsLib`, which runs anywhere. What is macOS-only is the test in [`mongfontbuilder/tests/test_templates.py`](../mongfontbuilder/tests/test_templates.py), which exports `hudum.glyphs` to an OTF through the `glyphs` command-line tool of the Glyphs app; the test is skipped on other platforms.

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the contribution workflow.
