import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import svelte from "@astrojs/svelte";

export default defineConfig({
  trailingSlash: "always",
  integrations: [
    svelte(),
    starlight({
      title: "Encoding and Shaping of the Mongolian Script",
      sidebar: [
        "index",
        "introduction",
        "architecture",
        "toolchain",
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
        "unified-writing-system",
        "digits-and-punctuation",
        "comparison",
        "modifications",
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
        Banner: "./src/Banner.astro",
        Footer: "./src/Footer.astro",
        ThemeProvider: "./src/ThemeProvider.astro",
        ThemeSelect: "./src/ThemeSelect.astro",
      },
    }),
  ],
});
