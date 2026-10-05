<script lang="ts">
  import { locales, type LocaleID } from "../../data/locales";
  import { writtenUnits } from "../../data/writtenUnits";

  interface Props {
    MNG?: boolean;
    MNGx?: boolean;
    TOD?: boolean;
    TODx?: boolean;
    SIB?: boolean;
    MCH?: boolean;
    MCHx?: boolean;
    links?: string;
    category?: string;
  }

  let { MNG, MNGx, TOD, TODx, SIB, MCH, MCHx, links = "", category = "" }: Props = $props();

  // The writing system is named by the attribute that is set, so that a citation reads
  // <Mong MNG links="..." /> rather than a component per writing system.
  const locale = $derived<LocaleID>(MNG ? "MNG" : MNGx ? "MNGx" : TOD ? "TOD" : TODx ? "TODx" : SIB ? "SIB" : MCH ? "MCH" : MCHx ? "MCHx" : "MNG");

  const prefix = $derived(locales[locale].name);
  const items = $derived(links.split(" ").filter(Boolean));

  // An archived revision is published under a base path (see `astro.config.ts`), so a
  // link into the site has to carry it; `BASE_URL` is that path, and is `/` otherwise.
  const base = import.meta.env.BASE_URL;

  // The format controls take part in the shaping of the letters around them rather than
  // being written forms of a writing system, so they are described in the chapter that
  // treats the character layer, not among the written forms of a writing system. An item
  // that names one is linked there whatever the writing system it was written for. Two of
  // them are also cited by the transcription they are written with, and not by name.
  const FORMAT_CONTROLS = new Set(["fvs", "fvs1", "fvs2", "fvs3", "fvs4", "mvs", "nnbsp", "nirugu", "zwj", "zwnj", "·", "–"]);

  // The free variation selectors are named by their number; render it as a superscript
  // (FVS1 → ¹) so the label reads as a variation of the selector rather than a separate unit.
  const CONTROL_LABELS: Record<string, string> = {
    fvs1: "¹",
    fvs2: "²",
    fvs3: "³",
    fvs4: "⁴",
  };

  const categoryItems = $derived(category ? locales[locale]?.categories?.[category as keyof (typeof locales)[typeof locale]["categories"]] || [] : []);
</script>

{#each items as item}
  {@const parts = item.split(".")}
  {@const isPos = parts.length >= 2 && parts[1] !== ""}
  {@const unit = isPos ? parts[0] : item}
  {@const pos = isPos ? parts[1] : ""}
  {@const fvs = isPos && parts.length >= 3 ? parts[2] : undefined}
  {@const isUnit = unit in writtenUnits}
  {@const isControl = FORMAT_CONTROLS.has(unit.toLowerCase())}
  {@const href = isControl ? `${base}architecture/#format-controls` : !isPos ? `${base}${prefix}/#${item}` : fvs === undefined ? (isUnit ? `${base}${prefix}/#${unit}-${pos}` : `${base}${prefix}/#${unit}-${pos}-0`) : `${base}${prefix}/#${unit}-${pos}-${fvs}`}
  {@const label = CONTROL_LABELS[unit.toLowerCase()] ?? (fvs === undefined ? item : fvs === "0" ? `${unit}.${pos} (default)` : `${unit}.${pos}.${fvs}`)}
  <a {href} style="font-style: {unit[0] === unit[0].toLowerCase() ? 'italic' : 'normal'}">{label}</a>
{/each}{#if categoryItems.length > 0}
  <span>
    {#each categoryItems as catItem, index}
      <a href={`${base}${prefix}/#${catItem}`} style="font-style: italic">{catItem}</a>{index < categoryItems.length - 1 ? ", " : ""}
    {/each}
  </span>
{/if}
