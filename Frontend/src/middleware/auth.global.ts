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

    const auth = useAuthStore();

    // ---------- SERVER (SSR) ----------
    if (process.server) {
      // Read cookies on server (available during SSR request)
      const token = useCookie<string | null>("access_token", {
        path: "/",
      }).value;
      const role = useCookie<Role | null>("user_role", { path: "/" }).value;

      // Set store so SSR render can reflect auth state
      auth.setToken(token ?? "");
      auth.setUser(role ? ({ role } as any) : null); // optional minimal user
      auth.setReady(true);

      if (isProtectedPath(to.path) && !token) {
        return navigateTo("/auth/login", { redirectCode: 302 });
      }

      // Role guard on server
      for (const [prefix, allowed] of Object.entries(routeRoles)) {
        if (to.path.startsWith(prefix) && (!role || !allowed.includes(role))) {
          return navigateTo("/auth/login", { redirectCode: 302 });
        }
      }

      return;
    }

    // ---------- CLIENT ----------
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

    const clientRole = auth.user?.role;
    for (const [prefix, allowed] of Object.entries(routeRoles)) {
      if (
        to.path.startsWith(prefix) &&
        (!clientRole || !allowed.includes(clientRole))
      ) {
        return navigateTo("/auth/login");
      }
    }
  }
);
