/**
 * Prefix the root-relative links of the documentation pages with the site's base path.
 *
 * A revision of the documentation that is archived under `UTN_REVISION` (see
 * `astro.config.ts`) is published under a base path of its own. Starlight applies that
 * path to the links it renders itself, but a link written in the prose as
 * `/architecture/` is left alone by the build, and would take the reader out of the
 * archive. This rewrites those links, and the `src` of an element that carries one.
 *
 * Astro's Markdown processor is Sätteri (`markdown.processor` in `astro.config.ts`), so
 * this is a hast plugin of that processor rather than a rehype one.
 */

import type { Element, Properties } from "hast";

/** The attributes that may hold a URL. */
const URL_ATTRIBUTES = ["href", "src"];

/** The elements the documentation can carry one of them on. */
const URL_ELEMENTS = ["a", "img"];

function withBase(properties: Properties, base: string): Properties | null {
  let rewritten: Properties | null = null;
  for (const attribute of URL_ATTRIBUTES) {
    const url = properties[attribute];
    // A root-relative URL begins with a single slash; `//host` is protocol-relative.
    if (typeof url === "string" && url.startsWith("/") && !url.startsWith("//")) {
      rewritten ??= { ...properties };
      rewritten[attribute] = base + url.slice(1);
    }
  }
  return rewritten;
}

export function baseLinks(base: string) {
  return {
    name: "base-links",
    element: {
      filter: URL_ELEMENTS,
      visit(node: Readonly<Element>) {
        const properties = withBase(node.properties, base);
        return properties === null ? undefined : { ...node, properties };
      },
    },
  };
}
