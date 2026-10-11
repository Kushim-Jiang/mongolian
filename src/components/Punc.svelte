<script lang="ts">
  import { punctuation } from "../../data/writtenUnits";
  import Cp from "./Cp.svelte";
  import Wu from "./Wu.svelte";

  interface Props {
    name: keyof typeof punctuation;
  }
  let { name }: Props = $props();

  const entry = $derived(punctuation[name]);
  const left = $derived(String.fromCodePoint(punctuation.Boundaryleft.code));
  const right = $derived(String.fromCodePoint(punctuation.Boundaryright.code));
  const unicode = $derived("unicode" in entry ? entry.unicode : undefined);
  const mark = $derived(String.fromCodePoint(entry.code));
</script>

<td
  >{#if unicode !== undefined}<Cp cp={unicode} />{/if}</td
>
<td>
  <Wu
    wrapperClass="wu-rotated"
    parts={[
      { text: left, class: "lig-gray" },
      { text: mark, class: "wu-box" },
      { text: right, class: "lig-gray" },
    ]}
  />
</td>
