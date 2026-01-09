import type { AuthService } from "~/api/iam/iam.service";

declare module "#app" {
  interface NuxtApp {
    $authService: AuthService;
  }
}

declare module "vue" {
  interface ComponentCustomProperties {
    $authService: AuthService;
  }
}

export {};