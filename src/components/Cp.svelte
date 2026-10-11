<script lang="ts">
  import Names from "@unicode/unicode-18.0.0/Names/index.mjs";
  import { hexFromCP } from "./utils";

  interface Props {
    /** The code point, as hex without `U+` or as a number, e.g. `200C`. */
    cp: string | number;
    /** Write the character name with the code point: `true` gives `U+180A MONGOLIAN NIRUGU`, `"pre"` gives `MONGOLIAN NIRUGU (U+180A)`. */
    name?: boolean | "pre";
    /** The name to write, for an abbreviated or otherwise shortened form; by default the Unicode name. */
    text?: string;
  }

  let { cp, name = false, text }: Props = $props();

  // The Unicode version the citations are made against.
  const UNICODE_VERSION = "18.0.0";

  // A nameslist page is named by the first code point of the block it covers, and the
  // blocks are not on a fixed stride, so the block that contains the code point is read
  // from the Unicode data instead of rounding the code point down to a multiple of 256.
  // Only the build reads it: the component is rendered on the server, not hydrated.
  const blockRanges = import.meta.glob("/node_modules/@unicode/unicode-18.0.0/Block/*/ranges.mjs", {
    eager: true,
  }) as Record<string, { default: { begin: number; end: number }[] }>;
  const blocks = Object.values(blockRanges).map(({ default: ranges }) => ranges[0]);

  const codePoint = $derived(typeof cp === "number" ? cp : Number.parseInt(cp, 16));
  const hex = $derived(hexFromCP(codePoint));
  const block = $derived(blocks.find((b) => codePoint >= b.begin && codePoint <= b.end));
  const url = $derived(block ? `https://www.unicode.org/Public/${UNICODE_VERSION}/charts/nameslist/${hexFromCP(block.begin).toLowerCase()}/#${hex.toLowerCase()}` : undefined);
  const written = $derived(text ?? Names.get(codePoint));
  const label = $derived(name === "pre" ? `${written} (U+${hex})` : name ? `U+${hex} ${written}` : `U+${hex}`);
</script>

{#if url}<a href={url}>{label}</a>{:else}{label}{/if}
