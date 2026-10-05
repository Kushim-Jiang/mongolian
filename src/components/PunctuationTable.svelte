<script lang="ts">
  import Names from "@unicode/unicode-18.0.0/Names/index.mjs";
  import type { LocaleID } from "../../data/locales";
  import { punctuation } from "../../data/writtenUnits";
  import Punc from "./Punc.svelte";

  // A column is a writing system together with the Ali Gali extension written with it, and
  // names the marks both of them write.
  const columns: { label: string; locales: LocaleID[] }[] = [
    { label: "Hudum with Ali Gali", locales: ["MNG", "MNGx"] },
    { label: "Todo with Ali Gali", locales: ["TOD", "TODx"] },
    { label: "Sibe", locales: ["SIB"] },
    { label: "Manchu with Ali Gali", locales: ["MCH", "MCHx"] },
  ];

  // The table is the punctuation of the data, in the order the data is written. An entry
  // without a code point is one of the boundaries a written form is quoted with, which is
  // not a character of the script.
  type Mark = {
    key: keyof typeof punctuation;
    name: string;
    locales: readonly LocaleID[];
  };

  const marks: Mark[] = [];
  for (const key of Object.keys(punctuation) as (keyof typeof punctuation)[]) {
    const entry = punctuation[key];
    if (!("unicode" in entry)) continue;
    marks.push({
      key,
      name:
        Names.get(entry.unicode) ??
        `U+${entry.unicode.toString(16).toUpperCase().padStart(4, "0")}`,
      locales: entry.locales,
    });
  }
</script>

<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Code point</th>
      <th>Written form</th>
      {#each columns as column}
        <th>{column.label}</th>
      {/each}
    </tr>
  </thead>
  <tbody>
    {#each marks as mark}
      <tr>
        <td>{mark.name}</td>
        <Punc name={mark.key} />
        {#each columns as column}
          <td
            >{column.locales.some((locale) => mark.locales.includes(locale))
              ? "✔"
              : ""}</td
          >
        {/each}
      </tr>
    {/each}
  </tbody>
</table>
