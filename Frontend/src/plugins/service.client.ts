// ~/plugins/services.client.ts
import { defineNuxtPlugin } from "nuxt/app";
import { AcademicService } from "~/services/academicService";
import { AcademicApi } from "~/api/academic/academic.api";
import { AdminService } from "~/services/adminService";
import { AdminApi } from "~/api/admin/admin.api";
import { AuthService } from "~/services/authService";
import { AuthApi } from "~/api/auth/auth.api";
import type { AxiosInstance } from "axios";
export default defineNuxtPlugin((nuxtApp: any) => {
  const api = nuxtApp.$api as AxiosInstance;
  nuxtApp.provide("academicService", new AcademicService(new AcademicApi(api)));
  nuxtApp.provide("adminService", new AdminService(new AdminApi(api)));
  nuxtApp.provide("authService", new AuthService(new AuthApi(api)));
});
