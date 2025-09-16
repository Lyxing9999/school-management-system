import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/api/types/enums/role.enum";
import type { RouteLocationNormalized } from "vue-router";

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
  (to: RouteLocationNormalized, from: RouteLocationNormalized) => {
    if (!process.client) return;

    const auth = useAuthStore();

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
