import tailwindcss from "@tailwindcss/vite";
import { defineNuxtConfig } from "nuxt/config";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

const isProd = process.env.NODE_ENV === "production";
const isAnalyze = process.env.ANALYZE === "true";
const isVercel = !!process.env.VERCEL;

let visualizerPlugin: any = null;
if (isAnalyze) {
  try {
    visualizerPlugin = require("rollup-plugin-visualizer").visualizer;
  } catch {
    visualizerPlugin = null;
  }
}

export default defineNuxtConfig({
  srcDir: "src/",
  compatibilityDate: "2025-05-29",
  ssr: true,

  modules: ["@element-plus/nuxt", "@pinia/nuxt"],
  css: ["~/styles/main.css", "~/styles/sidebar.scss"],
  devtools: { enabled: !isProd },

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
    },
  },
  devServer: !isProd ? { host: "0.0.0.0" } : undefined,
  vite: {
    plugins: [
      tailwindcss(),
      ...(visualizerPlugin
        ? [
            visualizerPlugin({
              open: true,
              gzipSize: true,
              brotliSize: true,
              filename: ".nuxt/stats.html",
            }),
          ]
        : []),
    ],

    server: !isProd ? { watch: { usePolling: true } } : undefined,
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
  },

  nitro: {
    preset: isVercel ? "vercel" : "node-server",
  },
});
