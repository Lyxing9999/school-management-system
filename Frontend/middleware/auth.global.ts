import { useAuthStore } from "~/stores/authStore";
import { UserRole } from "~/types/auth";

export default defineNuxtRouteMiddleware((to, from) => {
  if (!process.client) return;

  const auth = useAuthStore();

  if (!auth.isAuthenticated && !to.path.startsWith("/auth")) {
    return navigateTo("/auth/login");
  }
  const role = auth.user?.role;

  if (to.path.startsWith("/admin") && (!role || role !== UserRole.Admin)) {
    return navigateTo("/auth/login");
  }

  if (to.path.startsWith("/teacher") && (!role || role !== UserRole.Teacher)) {
    return navigateTo("/auth/login");
  }

  if (to.path.startsWith("/student") && (!role || role !== UserRole.Student)) {
    return navigateTo("/auth/login");
  }
});
