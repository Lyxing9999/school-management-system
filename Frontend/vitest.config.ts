import { defineConfig } from "vitest/config";
import { resolve } from "path";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.ts"],
  },
  resolve: {
    alias: {
      "~": resolve(__dirname, "."),
      "@": resolve(__dirname, "."),
      "#app": resolve(__dirname, "test/mocks/nuxt-app.ts"),
      "#imports": resolve(__dirname, "test/mocks/nuxt-imports.ts"),
      "#build/nuxt.config.mjs": resolve(__dirname, "test/mocks/nuxt-config.ts"),
    },
  },
  define: {
    "process.client": true,
    "process.server": false,
    "process.dev": true,
  },
  server: {
    deps: {
      inline: ["element-plus", "@element-plus/icons-vue"],
    },
  },
});
