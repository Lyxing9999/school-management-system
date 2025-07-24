import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import type { NuxtApp } from "nuxt/app";

export default defineNuxtPlugin((nuxtApp: NuxtApp) => {
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    nuxtApp.vueApp.component(key, component);
  }
});
