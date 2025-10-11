// ~/types/nuxt.d.ts
import { AdminService } from "~/services/adminService";
import { AcademicService } from "~/services/academicService";
import { AuthService } from "~/services/authService";

declare module "nuxt/app" {
  interface NuxtApp {
    $adminService: AdminService;
    $academicService: AcademicService;
    $authService: AuthService;
  }
}

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    $adminService: AdminService;
    $academicService: AcademicService;
    $authService: AuthService;
  }
}
