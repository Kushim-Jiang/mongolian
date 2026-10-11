<script lang="ts">
  interface Props {
    position: JoiningPosition;
    ctxPosition?: JoiningPosition;
    id?: WrittenUnitID;
    written?: WrittenUnitID[];
    charName?: string;
    fvs?: FVS;
    aliases?: string[];
  }

  let { position, ctxPosition, id, written, charName, fvs, aliases = [] }: Props = $props();

  import type { JoiningPosition } from "../../data/misc";
  import type { FVS } from "../../data/variants";
  import type { WrittenUnitID } from "../../data/writtenUnits";
  import { nameToCP, buildWrittenText, niText, ctxBefore, ctxAfter } from "./utils";
  import Wu from "./Wu.svelte";

  const units = $derived(id ? [id] : written);
  const effectiveCtx = $derived(ctxPosition ?? position);
  const showBefore = $derived(ctxBefore(effectiveCtx));
  const showAfter = $derived(ctxAfter(effectiveCtx));

  let text = $derived.by(() => {
    if (units) return buildWrittenText(units, position);
    if (charName) {
      let t = String.fromCodePoint(nameToCP.get(charName)!);
      if (fvs) t += ["\u{180B}", "\u{180C}", "\u{180D}", "\u{180F}"][fvs - 1];
      return t;
    }
    return "?";
  });
</script>

<Wu parts={[...(showBefore ? [{ text: niText("init"), class: "wu-context" }] : []), { text }, ...(showAfter ? [{ text: niText("fina"), class: "wu-context" }] : [])]} />
{#if aliases.length}
  <br />
  <i>
    {#each aliases as a, i}
      {i ? " " : ""}<a href="#{a}">{a}</a>
    {/each}
  </i>
{/if}
