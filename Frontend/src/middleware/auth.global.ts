// ~/src/middleware/auth.global.ts
import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/api/types/enums/role.enum";
import type { RouteLocationNormalizedLoaded } from "vue-router";

const routeRoles: Record<string, Role[]> = {
  "/admin": [Role.ADMIN],
  "/teacher": [Role.TEACHER],
  "/student": [Role.STUDENT],
  "/front-office": [Role.FRONT_OFFICE],
  "/academic": [Role.ACADEMIC],
  "/finance": [Role.FINANCE],
  "/parent": [Role.PARENT],
  "/hr": [Role.HR],
};

export default defineNuxtRouteMiddleware(
  (to: RouteLocationNormalizedLoaded) => {
    if (!process.client) return;

    const auth = useAuthStore();

    if (
      !to.path.startsWith("/auth") &&
      (to.path === "/" || to.path === "/home")
    ) {
      return navigateTo("/auth/login");
    }

    if (!auth.isAuthenticated && !to.path.startsWith("/auth")) {
      return navigateTo("/auth/login");
    }

    const role = auth.user?.role;

    for (const [prefix, allowedRoles] of Object.entries(routeRoles)) {
      if (
        to.path.startsWith(prefix) &&
        (!role || !allowedRoles.includes(role))
      ) {
        return navigateTo("/auth/login");
      }
    }
  }
);
