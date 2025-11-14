// ~/plugins/services.client.ts
import { defineNuxtPlugin } from "nuxt/app";
import { AcademicService } from "~/services/academicService";
import { AcademicApi } from "~/api/academic/academic.api";
import { AuthService } from "~/services/authService";
import { AuthApi } from "~/api/auth/api";
import type { AxiosInstance } from "axios";

export default defineNuxtPlugin((nuxtApp: any) => {
  const api = nuxtApp.$api as AxiosInstance;
  nuxtApp.provide("academicService", new AcademicService(new AcademicApi(api)));
  nuxtApp.provide("authService", new AuthService(new AuthApi(api)));
});
