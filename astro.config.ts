import { defineConfig, envField } from "astro/config";
import starlight from "@astrojs/starlight";
import svelte from "@astrojs/svelte";

const UTN_REVISION_STRING = process.env.UTN_REVISION;

export default defineConfig({
  env: {
    schema: {
      UTN_REVISION: envField.number({
        context: "server",
        access: "public",
        optional: true,
        int: true,
        min: 1,
      }),
    },
  },
  base: UTN_REVISION_STRING
    ? `/notes/tn57/utn57-mong-${UTN_REVISION_STRING}/`
    : undefined,
  trailingSlash: "always",
  integrations: [
    svelte(),
    starlight({
      title: "Encoding and Shaping of the Mongolian Script",
      sidebar: [
        "index",
        "architecture",
        {
          label: "Writing systems",
          items: [
            "hudum",
            "todo",
            "sibe",
            "manchu",
            "hudum-ali-gali",
            "todo-ali-gali",
            "manchu-ali-gali",
          ],
        },
        "non-joining-characters",
        "single-font-implementation",
        {
          label: "Appendices",
          items: ["background", "phonology", "unicode-standard", "comparison"],
        },
      ],
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/Kushim-Jiang/mongolian",
        },
      ],
      editLink: {
        baseUrl: "https://github.com/Kushim-Jiang/mongolian/edit/main/",
      },
      customCss: ["./src/custom.css"],
      components: {
        ThemeProvider: "./src/ThemeProvider.astro",
        ThemeSelect: "./src/ThemeSelect.astro",
      },
    }),
  ],
});
