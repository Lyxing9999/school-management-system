import { useAuthStore } from "~/stores/authStore";

function setAccessToken(token: string) {
  try {
    localStorage.setItem("access_token", token);
  } catch {}
}

function clearAccessToken() {
  try {
    localStorage.removeItem("access_token");
  } catch {}
}

export default defineNuxtPlugin(async () => {
  if (import.meta.server) return;

  const auth = useAuthStore();
  const route = useRoute();

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
      clearAccessToken();
      auth.resetForGuest();
      return;
    }

    setAccessToken(access);
    auth.setToken(access);

    const me = await $api.get("/api/iam/me");
    auth.setUser((me?.data as any)?.data ?? null);
  } catch {
    clearAccessToken();
    auth.resetForGuest();
  } finally {
    auth.setReady(true);
  }
});
