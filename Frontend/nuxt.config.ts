import tailwindcss from "@tailwindcss/vite";
import { visualizer } from "rollup-plugin-visualizer";
import { defineNuxtConfig } from "nuxt/config";

export default defineNuxtConfig({
  srcDir: "src/",
  compatibilityDate: "2025-05-29",

  modules: ["@element-plus/nuxt", "@pinia/nuxt"],
  devtools: true,

  css: ["~/styles/main.css", "~/styles/sidebar.scss"],

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
    head: {
      script: [
        {
          children: `(function(){try{
          var t=localStorage.getItem('theme')||'light';
          var r=(t==='light')?'dark':t;
          var el=document.documentElement;
          el.setAttribute('data-theme', r);
          if(r==='dark') el.classList.add('dark'); else el.classList.remove('dark');
        }catch(e){}})();`,
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
