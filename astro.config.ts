import { defineConfig, envField } from "astro/config";
import starlight from "@astrojs/starlight";
import svelte from "@astrojs/svelte";

export default defineConfig({
  env: {
    schema: {
      UTN: envField.boolean({
        context: "server",
        access: "public",
        optional: true,
      }),
    },
  },
  trailingSlash: "always",
  integrations: [
    svelte(),
    starlight({
      title: "Encoding and Shaping of the Mongolian Script",
      sidebar: [
        "index",
        "toolchain",
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
          items: ["background", "unicode-standard", "comparison"],
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
