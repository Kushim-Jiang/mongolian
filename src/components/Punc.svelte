<script lang="ts">
  import { punctuation } from "../../data/writtenUnits";

  interface Props {
    name: keyof typeof punctuation;
  }
  let { name }: Props = $props();

  const entry = $derived(punctuation[name]);
  const left = $derived(String.fromCodePoint(punctuation.Boundaryleft.code));
  const right = $derived(String.fromCodePoint(punctuation.Boundaryright.code));
  const unicode = $derived("unicode" in entry ? entry.unicode : undefined);
  const mark = $derived(String.fromCodePoint(entry.code));
  const codepoint = $derived(unicode === undefined ? "" : `U+${unicode.toString(16).toUpperCase().padStart(4, "0")}`);
</script>

<td>{codepoint}</td>
<td>
  <span class="wu wu-rotated">
    <span class="wu-gray">{left}</span><span class="wu-box">{mark}</span><span class="wu-gray">{right}</span>
  </span>
</td>

<style>
  .wu-rotated {
    display: inline-block;
    white-space: nowrap;
    transform: rotate(90deg);
    padding: 10pt 0pt;
  }

  .wu-gray {
    color: var(--helper-gray);
  }

  .wu-box {
    display: inline-block;
    white-space: pre;
    border: 2px solid var(--helper-blue);
    margin: 0 1px;
    transform: translateY(-1px);
  }
</style>
