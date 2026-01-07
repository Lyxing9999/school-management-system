import { useAuthStore } from "~/stores/authStore";

export default defineNuxtPlugin(async () => {
  if (import.meta.server) return;

  const auth = useAuthStore();
  const route = useRoute();

  // always mark ready on auth pages (login/register/reset)
  if (route.path.startsWith("/auth")) {
    auth.setReady(true);
    return;
  }

  auth.setReady(false);

  try {
    const { $api } = useNuxtApp();

    const r = await $api.post("/api/iam/refresh");
    const access = (r?.data as any)?.access_token as string | undefined;

    if (!access) {
      auth.resetForGuest();
      return;
    }

    auth.setToken(access);

    const me = await $api.get("/api/iam/me");
    auth.setUser((me?.data as any)?.data ?? null);
  } catch {
    auth.resetForGuest();
  } finally {
    auth.setReady(true);
  }
});
