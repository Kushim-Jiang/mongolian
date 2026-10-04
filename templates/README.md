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

Template generation requires the Glyphs app via `glyphsLib`, so it is **macOS-only**, and the tests in [`mongfontbuilder/tests/test_templates.py`](../mongfontbuilder/tests/test_templates.py) are skipped on other platforms.

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the contribution workflow.
