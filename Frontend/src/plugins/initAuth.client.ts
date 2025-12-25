import { useAuthStore } from "~/stores/authStore";

export default defineNuxtPlugin(async () => {
  if (!process.client) return;

  const path = window.location.pathname;
  if (path.startsWith("/auth")) return; 

  const authStore = useAuthStore();
  const { $api } = useNuxtApp();

  if (!authStore.token) {
    try {
      const r = await $api.post("/api/iam/refresh");
      authStore.setToken(r.data.access_token);

      const me = await $api.get("/api/iam/me");
      authStore.setUser(me.data);
    } catch {
      authStore.clear();
    } finally {
      authStore.setReady(true);
    }
  } else {
    authStore.setReady(true);
  }
});
