<script lang="ts">
  interface Props {
    locale: LocaleID | LocaleID[];
    /** Letters that lie outside the writing systems, which this table lists in place. */
    outside?: OutsideLetters;
  }
  let { locale, outside = {} }: Props = $props();

  import type { LocaleID } from "../../data/locales";
  import type { JoiningPosition } from "../../data/misc";
  import type { FVS, VariantData } from "../../data/variants";
  import type { WrittenUnitID } from "../../data/writtenUnits";
  import type { OutsideLetters } from "../../data/outsideLetters";
  import { joiningPositions } from "../../data/misc";
  import { variants } from "../../data/variants";
  import { aliases } from "../../data/aliases";
  import LetterVariant from "./LetterVariant.svelte";
  import { hexFromCP, nameToCP } from "./utils";
  import { localeNS, orderedAliases, resolveCharName, mapGetOrCreate, isVariantRef, sortedFVSKeys } from "./utils";

  type LocalizedVariant = { written: VariantData["written"]; resolvedWritten?: WrittenUnitID[]; archaic: boolean; unrecommended: boolean };
  /** The data of one joining position of a letter that lies outside the writing systems. */
  type OutsideVariant = { fvs: FVS; written: VariantData["written"]; resolvedWritten?: WrittenUnitID[]; unrecommended: boolean };
  const localesToShow = $derived(Array.isArray(locale) ? locale : [locale]);
  /** A unified table merges the writing systems, so each character is listed once. */
  const unified = $derived(localesToShow.length > 1);

  /** The shapes a cell shows: one entry per distinct shape, with the writing systems
      that share it. A real shape covers the fabricated ones — shapes borrowed from
      another joining position — and conflicting fabricated shapes reduce to the first
      one in order. The writing systems a covered shape belonged to are named after the
      shape that covers them. */
  function shapesOfCell(localeToVariant: Map<LocaleID, LocalizedVariant> | undefined): { variant: LocalizedVariant; locales: LocaleID[]; covered: LocaleID[] }[] {
    const groups = new Map<string, { variant: LocalizedVariant; locales: LocaleID[] }>();
    for (const [locale, variant] of localeToVariant ?? []) {
      const key = JSON.stringify([variant.written, variant.resolvedWritten ?? null]);
      const group = groups.get(key);
      if (group) group.locales.push(locale);
      else groups.set(key, { variant, locales: [locale] });
    }

    const shapes = [...groups.entries()];
    const real = shapes.filter(([, i]) => !isVariantRef(i.variant.written));
    const shown = real.length ? real : shapes.slice(0, 1);
    const shownKeys = new Set(shown.map(([key]) => key));
    const covered = shapes.filter(([key]) => !shownKeys.has(key)).flatMap(([, i]) => i.locales);

    return shown.map(([, shape], index) => ({ ...shape, covered: index === 0 ? covered : [] }));
  }

  const charNameToPositionToFVSToLocaleToLocalizedVariant = $derived.by(() => {
    const map = new Map<string, Map<JoiningPosition, Map<FVS, Map<LocaleID, LocalizedVariant>>>>();

    for (const locale of localesToShow) {
      const _localeNamespace = localeNS(locale);
      for (const alias of orderedAliases(locale)) {
        const charName = resolveCharName(alias, _localeNamespace);
        if (!charName) continue;
        const positionToFVSToVariant = variants[charName];
        for (const position of joiningPositions) {
          for (const [fvs, variant] of Object.entries(positionToFVSToVariant[position])) {
            const variantLocaleData = variant.locales[locale];
            if (!variantLocaleData) continue;
            const positionToFVSToData = mapGetOrCreate(map, charName, () => new Map());
            const fvsToData = mapGetOrCreate(positionToFVSToData, position, () => new Map());
            const localeToData = mapGetOrCreate(fvsToData, Number(fvs) as FVS, () => new Map());
            localeToData.set(locale, {
              written: variantLocaleData.written ?? variant.written,
              archaic: variantLocaleData.archaic ?? false,
              unrecommended: variantLocaleData.unrecommended ?? false,
            });
          }
        }
      }
    }

    // Resolve VariantReferences, within the writing system that makes them.
    for (const positionToFVSToData of map.values()) {
      for (const fvsToLocaleToData of positionToFVSToData.values()) {
        for (const localeToData of fvsToLocaleToData.values()) {
          for (const [locale, data] of localeToData) {
            if (isVariantRef(data.written)) {
              const [refPos, refFvs] = data.written as unknown as [JoiningPosition, FVS];
              const refData = positionToFVSToData.get(refPos)?.get(refFvs)?.get(locale);
              if (refData) {
                if (isVariantRef(refData.written)) {
                  const [r2Pos, r2Fvs] = refData.written as unknown as [JoiningPosition, FVS];
                  const r2 = positionToFVSToData.get(r2Pos)?.get(r2Fvs)?.get(locale);
                  if (r2 && !isVariantRef(r2.written)) data.resolvedWritten = r2.written as WrittenUnitID[];
                } else {
                  data.resolvedWritten = refData.written as WrittenUnitID[];
                }
              }
            }
          }
        }
      }
    }

    return map;
  });

  /**
   * The letters that lie outside the writing systems, each position resolved the way a
   * position of a character is: a position that borrows the form of another position carries
   * the written units that position is drawn with. The table shows one form per position,
   * which is the first the data lists.
   */
  const charNameToOutsidePositionToVariant = $derived.by(() => {
    const map = new Map<string, Map<JoiningPosition, OutsideVariant>>();
    for (const [charName, positionToFVSToData] of Object.entries(outside)) {
      const positionToVariant = mapGetOrCreate(map, charName, () => new Map<JoiningPosition, OutsideVariant>());
      for (const position of joiningPositions) {
        if (positionToVariant.has(position)) continue;
        const [fvs, data] = Object.entries(positionToFVSToData[position])[0];
        if (!data) continue;
        const variant: OutsideVariant = { fvs: Number(fvs) as FVS, written: data.written, unrecommended: data.unrecommended ?? false };
        if (isVariantRef(data.written)) {
          const [refPosition, refFvs] = data.written;
          const refData = positionToFVSToData[refPosition][refFvs];
          if (refData && !isVariantRef(refData.written)) variant.resolvedWritten = refData.written;
        }
        positionToVariant.set(position, variant);
      }
    }
    return map;
  });

  /** A row of the table: a character of the writing systems, or a letter outside them. */
  type Row = {
    codePoint: number;
    charName: string;
    positionToFVSToData?: Map<JoiningPosition, Map<FVS, Map<LocaleID, LocalizedVariant>>>;
    letter?: Map<JoiningPosition, OutsideVariant>;
  };

  /**
   * The rows of the table: the characters in the order the data lists them, and the
   * letters that lie outside the writing systems. A unified table lists them by code
   * point instead, which is the order that interleaves the writing systems.
   */
  const rows = $derived.by(() => {
    const unknown = Number.POSITIVE_INFINITY;
    const rows: Row[] = [...charNameToPositionToFVSToLocaleToLocalizedVariant].map(([charName, positionToFVSToData]) => ({
      codePoint: nameToCP.get(charName) ?? unknown,
      charName,
      positionToFVSToData,
    }));
    if (!unified) return rows;
    for (const [charName, letter] of charNameToOutsidePositionToVariant) {
      rows.push({ codePoint: nameToCP.get(charName) ?? unknown, charName, letter });
    }
    return rows.sort((i, j) => i.codePoint - j.codePoint);
  });
</script>

<table class="characters">
  <colgroup>
    <col class="letter" />
    <col class="fvs" />
    <col class="variant" />
    <col class="variant" />
    <col class="variant" />
    <col class="variant" />
  </colgroup>
  <thead>
    <tr><th rowspan="2">Letter</th><th rowspan="2">FVS</th><th colspan="4">Variants</th></tr>
    <tr
      >{#each joiningPositions as p}<th>{p}</th>{/each}</tr
    >
  </thead>
  <tbody>
    {#each rows as { charName, positionToFVSToData, letter }}
      {#if letter}
        {@render outsideRow(charName, letter)}
      {:else if positionToFVSToData}
        {@const codePoint = nameToCP.get(charName)!}
        {@const hex = hexFromCP(codePoint)}
        {@const char = String.fromCodePoint(codePoint)}
        {@const aliasData = aliases[charName]}
        {@const aliasesOfChar = localesToShow.map((l) => [l, (typeof aliasData === "object" ? aliasData[localeNS(l)] : aliasData) ?? ""] as const).filter(([, a]) => a)}
        {@const alias = aliasesOfChar[0]?.[1] ?? ""}
        {@const fvses = sortedFVSKeys(positionToFVSToData)}
        <tr>
          <td id={alias} rowspan={fvses.length + 1} title="U+{hex} {char} {charName}">
            {hex}<br />{char}{#if !unified}{" "}
              <i>{alias}</i>{/if}
          </td>
          {@render variantCells(charName, positionToFVSToData, 0, alias)}
        </tr>
        {#each fvses as fvs}
          <tr>{@render variantCells(charName, positionToFVSToData, fvs, alias)}</tr>
        {/each}
      {/if}
    {/each}
  </tbody>
</table>

{#snippet outsideRow(charName: string, positionToVariant: Map<JoiningPosition, OutsideVariant>)}
  {@const codePoint = nameToCP.get(charName)!}
  {@const hex = hexFromCP(codePoint)}
  {@const char = String.fromCodePoint(codePoint)}
  <tr>
    <td id={charName} title="U+{hex} {char} {charName}">{hex}<br />{char}</td>
    <td>-</td>
    {#each joiningPositions as position}
      {@const variant = positionToVariant.get(position)}
      {@const ref = variant && isVariantRef(variant.written) ? (variant.written as [JoiningPosition, FVS]) : undefined}
      {@const written = variant && !ref ? (variant.written as WrittenUnitID[]) : undefined}
      <td id={`${charName}-${position}-${variant?.fvs ?? 0}`} class={{ variant: true, fabricated: !!ref, unrecommended: variant?.unrecommended }}>
        {#if ref}
          <span><LetterVariant position={ref[0]} ctxPosition={position} written={variant?.resolvedWritten} /></span><br />
          <a href="#{charName}-{ref[0]}-{ref[1]}">→ {ref[0]}{ref[1] ? ` ${ref[1]}` : ""}</a>
        {:else}
          <span><LetterVariant {position} {written} /></span><br />
          {#each written ?? [] as unit, unitIndex}{unitIndex ? " " : ""}<a href="#{unit}">{unit}</a>{/each}
        {/if}
      </td>
    {/each}
  </tr>
{/snippet}

{#snippet variantCells(charName: string, positionToFVSToData: Map<JoiningPosition, Map<FVS, Map<LocaleID, LocalizedVariant>>>, fvs: FVS, alias: string)}
  <td>{fvs || "-"}</td>
  {#each positionToFVSToData as [position, fvsToLocaleToData]}
    {@const groups = shapesOfCell(fvsToLocaleToData.get(fvs))}
    {@const first = groups[0]?.variant}
    <td id={`${alias}-${position}-${fvs}`} class={{ variant: true, undefined: !first, fabricated: first ? isVariantRef(first.written) : false, archaic: first?.archaic, unrecommended: first?.unrecommended }}>
      {#each groups as { variant, locales: shapeLocales, covered }, index}
        {#if index}<br />{/if}
        {#if unified}
          <span class="locale-label"
            >{shapeLocales.join(" ")}{#if covered.length}{" "}({covered.join(" ")}){/if}</span
          >
        {/if}
        {#if isVariantRef(variant.written)}
          {@const ref = variant.written as [JoiningPosition, FVS]}
          {@const refPos = ref[0]}
          {@const refFvs = ref[1]}
          <span><LetterVariant {charName} position={refPos} ctxPosition={position} {fvs} written={variant.resolvedWritten} /></span><br />
          <a href="#{alias}-{refPos}-{refFvs}">→ {refPos}{refFvs ? ` ${refFvs}` : ""}</a>
        {:else}
          <span><LetterVariant {charName} {position} {fvs} written={variant.resolvedWritten ?? (variant.written as WrittenUnitID[])} /></span><br />
          {#each variant.written as unit, unitIndex}{unitIndex ? " " : ""}<a href="#{unit}">{unit}</a>{/each}
        {/if}
      {/each}
    </td>
  {/each}
{/snippet}

<style>
  td,
  th {
    text-align: center !important;
    vertical-align: middle;
  }
  td.variant span {
    line-height: 1;
  }
  td.fabricated,
  td.undefined {
    background-color: whitesmoke;
  }
  td.archaic {
    background-color: beige;
  }
  td.unrecommended {
    background-color: pink;
  }
  td:target {
    background-color: yellow;
  }
  td a {
    text-decoration: none;
  }
  td:nth-child(-n + 2) {
    width: 2rem;
  }
  td:nth-child(n + 3) {
    width: 4rem;
  }
</style>
