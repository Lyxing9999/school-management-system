import tailwindcss from "@tailwindcss/vite";
import { visualizer } from "rollup-plugin-visualizer";
import { defineNuxtConfig } from "nuxt/config";

const isProd = process.env.NODE_ENV === "production";
const isAnalyze = process.env.ANALYZE === "true";
const isVercel = !!process.env.VERCEL;

export default defineNuxtConfig({
  srcDir: "src/",
  compatibilityDate: "2025-05-29",

  ssr: true,

  modules: ["@element-plus/nuxt", "@pinia/nuxt"],

  devtools: {
    enabled:
      process.env.NODE_ENV === "development" || process.env.NUXT_DEV === "true",
  },

  css: ["~/styles/main.css", "~/styles/sidebar.scss"],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "",
      calendarificApiKey: process.env.NUXT_PUBLIC_CALENDARIFIC_API_KEY || "",
    },
  },

  app: {
    head: {
      htmlAttrs: { lang: "en" },
      title: "School System",
      titleTemplate: "%s · School System",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
        {
          name: "description",
          content:
            "School management dashboard for attendance, grades, and schedules.",
        },
      ],

      script: [],
    },
  },

  vite: {
    plugins: [
      tailwindcss(),
      ...(isAnalyze
        ? [
            visualizer({
              open: true,
              gzipSize: true,
              brotliSize: true,
              filename: ".nuxt/stats.html",
            }),
          ]
        : []),
    ],

    define: {
      __DEV__: !isProd,
    },

    server: !isProd
      ? {
          watch: { usePolling: true },
          host: "0.0.0.0",
        }
      : undefined,

    optimizeDeps: !isProd
      ? {
          include: [
            "lodash-es",
            "@fullcalendar/core",
            "@fullcalendar/daygrid",
            "@fullcalendar/interaction",
          ],
        }
      : undefined,

    build: {
      sourcemap: true,

      minify: "esbuild",

      rollupOptions: {
        output: {
          /*
          manualChunks(id: string) {
            if (!id.includes("node_modules")) return;
            if (id.includes("element-plus")) return "vendor_element-plus";
            return "vendor";
          },
          */
        },
      },
    },

    esbuild: isProd ? { drop: ["console", "debugger"] } : undefined,
  },

  nitro: {
    preset: isVercel ? "vercel" : "node-server",
  },
});
