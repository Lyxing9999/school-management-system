import tailwindcss from "@tailwindcss/vite";
import { visualizer } from "rollup-plugin-visualizer";
import { defineNuxtConfig } from "nuxt/config";

export default defineNuxtConfig({
  srcDir: "src/",

  compatibilityDate: "2025-05-29",

  modules: ["@element-plus/nuxt", "@pinia/nuxt"],

  devtools: true,

  css: [
    "~/styles/main.css",
    "~/styles/element-overrides.css",
    "element-plus/dist/index.css",
  ],

  vite: {
    plugins: [tailwindcss(), visualizer({ open: false })],
    define: {
      __DEV__: true,
    },
    server: {
      watch: { usePolling: true },
      host: "0.0.0.0",
    },
  },

  ssr: false,

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE,
      calendarificApiKey: process.env.NUXT_PUBLIC_CALENDARIFIC_API_KEY,
    },
  },

  router: {
    middleware: ["auth"],
  },

  darkMode: "class",

  optimizeDeps: {
    include: [
      "lodash-es",
      "@fullcalendar/core",
      "@fullcalendar/daygrid",
      "@fullcalendar/interaction",
    ],
  },

  app: {
    baseURL: "/",
    head: {
      script: [
        {
          children: `(function() {
            try {
              if (localStorage.getItem('dark') === 'true') {
                document.documentElement.classList.add('dark');
              }
            } catch(_) {}
          })();`,
        },
      ],
    },
  },

  test: {
    globals: true,
    environment: "jsdom",
    vite: true,
    setupFiles: "./src/test/setup.ts",
    deps: {
      inline: ["element-plus"],
    },
  },

  nitro: {
    preset: "vercel",
  },
});
