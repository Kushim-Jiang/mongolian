import { glob } from "astro/loaders";
import { i18nLoader } from "@astrojs/starlight/loaders";
import { docsSchema, i18nSchema } from "@astrojs/starlight/schema";
import { defineCollection } from "astro:content";

export const collections = {
  docs: defineCollection({
    loader: glob({ pattern: "**/*.mdx", base: "docs" }),
    schema: docsSchema(),
  }),
  // Starlight always reads the `i18n` collection for the UI strings it lets a site
  // override. This site overrides none, but the collection has to be defined and hold
  // at least one entry, so `src/content/i18n/en.json` is an empty override.
  i18n: defineCollection({
    loader: i18nLoader(),
    schema: i18nSchema(),
  }),
};
