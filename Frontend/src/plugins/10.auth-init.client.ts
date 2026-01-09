import { useCookie } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";
import type { Role } from "~/api/types/enums/role.enum";

type AuthCookieUser = { id: string; username?: string; role: Role };

export default defineNuxtPlugin(() => {
  const auth = useAuthStore();

  const tokenCookie = useCookie<string | null>("access_token", {
    sameSite: "lax",
    path: "/",
  });

  const userCookie = useCookie<AuthCookieUser | null>("user_cache", {
    sameSite: "lax",
    path: "/",
  });

  auth.setToken(tokenCookie.value ?? "");
  auth.setUser((userCookie.value as any) ?? null);
  auth.setReady(true);
});
