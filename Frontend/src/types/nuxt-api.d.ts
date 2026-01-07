import type { AxiosInstance } from "axios";

declare module "#app" {
  interface NuxtApp {
    $api: AxiosInstance;
  }
}

declare module "nuxt/app" {
  interface NuxtApp {
    $api: AxiosInstance;
  }
}

declare module "vue" {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}

export {};
