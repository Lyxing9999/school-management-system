import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/api/types/enums/role.enum";
import type { RouteLocationNormalized } from "vue-router";
import { watch } from "vue";

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
  async (to: RouteLocationNormalized) => {
    if (import.meta.server) return;

    const auth = useAuthStore();

    if (!auth.isReady) {
      await new Promise<void>((resolve) => {
        const stop = watch(
          () => auth.isReady,
          (ready) => {
            if (ready) {
              stop();
              resolve();
            }
          },
          { immediate: true }
        );
      });
    }

    if (to.path.startsWith("/auth")) return;

    if ((to.path === "/" || to.path === "/home") && !auth.isAuthenticated) {
      return navigateTo("/auth/login");
    }

    if (!auth.isAuthenticated) return navigateTo("/auth/login");

    const role = auth.user?.role;
    for (const [prefix, allowed] of Object.entries(routeRoles)) {
      if (to.path.startsWith(prefix) && (!role || !allowed.includes(role))) {
        return navigateTo("/auth/login");
      }
    }
  }
);
