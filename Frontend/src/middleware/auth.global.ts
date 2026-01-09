import { useAuthStore } from "~/stores/authStore";
import { Role } from "~/api/types/enums/role.enum";
import { watch } from "vue";
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

const isProtectedPath = (path: string) =>
  path === "/" ||
  path === "/home" ||
  Object.keys(routeRoles).some((prefix) => path.startsWith(prefix));

export default defineNuxtRouteMiddleware(
  async (to: RouteLocationNormalized) => {

    if (to.path.startsWith("/auth")) return;

    if (process.server) {
      if (isProtectedPath(to.path)) {
        return navigateTo("/auth/login", { redirectCode: 302 });
      }
      return;
    }

    // client side
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

    if (isProtectedPath(to.path) && !auth.isAuthenticated) {
      return navigateTo("/auth/login");
    }

    const role = auth.user?.role;
    for (const [prefix, allowed] of Object.entries(routeRoles)) {
      if (to.path.startsWith(prefix) && (!role || !allowed.includes(role))) {
        return navigateTo("/auth/login");
      }
    }
  }
);
