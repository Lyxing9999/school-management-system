export default defineNuxtPlugin(() => {
  if (!import.meta.server) return;

  const { $api } = useNuxtApp();
  if (!$api) return;

  // same cookie name you set in AuthService
  const token = useCookie<string | null>("access_token", {
    sameSite: "lax",
    path: "/",
  }).value;

  if (token) {
    // apply to SSR API calls
    ($api.defaults.headers as any) = $api.defaults.headers ?? {};
    ($api.defaults.headers as any).common =
      ($api.defaults.headers as any).common ?? {};
    ($api.defaults.headers as any).common.Authorization = `Bearer ${token}`;
  }
});
