<script lang="ts">
  /** A run of glyphs a figure draws as one written form. */
  interface Part {
    text: string;
    /** The class that colours it: `lig-gray` a neighbour, `wu-context` the nirugu, none the form under discussion. */
    class?: string;
  }

  interface Props {
    /** The glyphs the figure is drawn with. */
    parts?: Part[];
    /**
     * The written units a figure quotes, in order, as hexadecimal code points, space
     * separated. The unit under discussion is written plain; a neighbouring unit is
     * prefixed with `~` (grey), and the nirugu with `+` (blue).
     */
    units?: string;
    /** A class for the figure itself, such as the `wu-rotated` a punctuation figure is drawn with. */
    wrapperClass?: string;
  }

  let { parts, units, wrapperClass = "" }: Props = $props();

  const ROLE_CLASS: Record<string, string> = { context: "lig-gray", nirugu: "wu-context" };

  const drawn = $derived(
    parts ??
      (units ?? "")
        .split(/\s+/)
        .filter(Boolean)
        .map((token) => ({
          text: String.fromCodePoint(Number.parseInt(token.replace(/^[~+]/, ""), 16)),
          class: ROLE_CLASS[token.startsWith("~") ? "context" : token.startsWith("+") ? "nirugu" : "form"] ?? "",
        })),
  );
</script>

<span class={wrapperClass ? `wu ${wrapperClass}` : "wu"}
  >{#each drawn as part}<span class={part.class ?? ""}>{part.text}</span>{/each}</span
>
