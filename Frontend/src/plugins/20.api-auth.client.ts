import type {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { useAuthStore } from "~/stores/authStore";

type RetryConfig = AxiosRequestConfig & { _retry?: boolean };
type PendingRequest = {
  request: RetryConfig;
  resolve: (value: unknown) => void;
  reject: (reason?: any) => void;
};

export default defineNuxtPlugin(() => {
  if (import.meta.server) return;

  const { $api } = useNuxtApp();
  if (!$api) return;

  const auth = useAuthStore();
  const tokenCookie = useCookie<string | null>("access_token", {
    sameSite: "lax",
    path: "/",
  });
  const roleCookie = useCookie<string | null>("user_role", {
    sameSite: "lax",
    path: "/",
  });
  const userCookie = useCookie<Record<string, any> | null>("user_cache", {
    sameSite: "lax",
    path: "/",
  });

  function clearAuthSession() {
    tokenCookie.value = null;
    roleCookie.value = null;
    userCookie.value = null;
    auth.resetForGuest();
  }

  $api.interceptors.request.use((cfg: InternalAxiosRequestConfig) => {
    const token = auth.token;

    if (token) {
      cfg.headers = cfg.headers ?? {};
      (cfg.headers as any).Authorization = `Bearer ${token}`;
    }

    return cfg;
  });

  let isRefreshing = false;
  let queue: PendingRequest[] = [];

  function flushQueue(newToken: string) {
    const pending = queue.slice();
    queue = [];
    for (const item of pending) {
      item.request.headers = item.request.headers ?? {};
      (item.request.headers as any).Authorization = `Bearer ${newToken}`;
      item.resolve($api(item.request));
    }
  }

  function rejectQueue(error: unknown) {
    const pending = queue.slice();
    queue = [];
    for (const item of pending) {
      item.reject(error);
    }
  }

  $api.interceptors.response.use(
    (res: AxiosResponse) => res,
    async (error: AxiosError) => {
      if (!error.response) return Promise.reject(error);

      const original = (error.config || {}) as RetryConfig;
      const status = error.response.status;

      const url = String(original.url || "");
      const isAuthRoute =
        url.includes("/api/iam/login") || url.includes("/api/iam/refresh");

      if (status !== 401 || isAuthRoute) return Promise.reject(error);

      if (original._retry) {
        clearAuthSession();
        return Promise.reject(error);
      }
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          queue.push({ request: original, resolve, reject });
        });
      }

      isRefreshing = true;

      try {
        const r = await $api.post("/api/iam/refresh");
        const newToken = (r.data as any)?.access_token as string | undefined;

        if (!newToken) {
          rejectQueue(error);
          clearAuthSession();
          isRefreshing = false;
          return Promise.reject(error);
        }

        auth.setToken(newToken);
        tokenCookie.value = newToken;

        isRefreshing = false;
        flushQueue(newToken);

        original.headers = original.headers ?? {};
        (original.headers as any).Authorization = `Bearer ${newToken}`;
        return $api(original);
      } catch (refreshErr) {
        isRefreshing = false;
        rejectQueue(refreshErr);
        clearAuthSession();
        return Promise.reject(refreshErr);
      }
    }
  );
});
