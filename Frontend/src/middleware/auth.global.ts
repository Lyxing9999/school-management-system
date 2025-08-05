import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/types";
import type { RouteLocationNormalized } from "vue-router";

export default defineNuxtRouteMiddleware(
  (to: RouteLocationNormalized, from: RouteLocationNormalized) => {
    console.log("to", to);
    console.log("from", from);
    if (!process.client) return;

    const auth = useAuthStore();

    if (!auth.isAuthenticated && !to.path.startsWith("/auth")) {
      return navigateTo("/auth/login");
    }
    const role = auth.user?.role;

    if (to.path.startsWith("/admin") && (!role || role !== Role.ADMIN)) {
      return navigateTo("/auth/login");
    }

    if (to.path.startsWith("/teacher") && (!role || role !== Role.TEACHER)) {
      return navigateTo("/auth/login");
    }

    if (to.path.startsWith("/student") && (!role || role !== Role.STUDENT)) {
      return navigateTo("/auth/login");
    }
  }
);
