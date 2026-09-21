# Test data

## The cases

- `core-*.tsv` — the core test suite of the Chinese national standard, one file per writing system: `hud` and `hag` (Hudum and its Ali Gali), `tod` and `tag` (Todo and its Ali Gali), `sib` (Sibe), and `man` and `mag` (Manchu and its Ali Gali);
- `eac-hud.tsv` — the EAC test suite, which is settled by the Hudum standard alone, in the form the suite reads it.

## The names the cases and the fonts are written with

`bases.yaml`, `marks.yaml`, and `format-controls.yaml` map the names the test fonts carry — the bases and the signs, the marks, the format controls — to the names of the written units they stand for. `utils.py` reads them into the mapping it parses the shaped fonts with.

## Files kept for reference

Nothing reads these; they are kept as the material the cases and the names above came from.

- `eac-hud.json`, `eac-tod.json`, `eac-sib.json`, `eac-man.json` — the EAC test suites as they are published, one file per writing system, of which `eac-hud.tsv` is the one the suite reads. The documentation of the model quotes `eac-hud.json` as the test data of the national standard.
  - eac-hud.json: [xunifont_rulewords_mon.js](http://rule.xueruhai.com/ruletest/xunifont_rulewords_mon.js) of [Hudum](http://rule.xueruhai.com/ruletest-mon.php)
  - eac-tod.json: [xunifont_rulewords_todo.js](http://rule.xueruhai.com/ruletest/xunifont_rulewords_todo.js) of [Todo](http://rule.xueruhai.com/ruletest-todo.php)
  - eac-sib.json: [xunifont_rulewords_sibe.js](http://rule.xueruhai.com/ruletest/xunifont_rulewords_sibe.js) of [Sibe](http://rule.xueruhai.com/ruletest-sibe.php)
  - eac-man.json: [xunifont_rulewords_man.js](http://rule.xueruhai.com/ruletest/xunifont_rulewords_man.js) of [Manchu](http://rule.xueruhai.com/ruletest-man.php)
- `menksoft.yaml` — the private-use code points of the Menksoft fonts, read against the glyph names that stand for them.
