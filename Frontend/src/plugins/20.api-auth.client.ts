import type {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { useAuthStore } from "~/stores/authStore";

type RetryConfig = AxiosRequestConfig & { _retry?: boolean };

export default defineNuxtPlugin(() => {
  if (import.meta.server) return;

  const { $api } = useNuxtApp();
  if (!$api) return;

  const auth = useAuthStore();

  $api.interceptors.request.use((cfg: InternalAxiosRequestConfig) => {
    const token = auth.token;

    if (token) {
      cfg.headers = cfg.headers ?? {};
      (cfg.headers as any).Authorization = `Bearer ${token}`;
    }

    return cfg;
  });

  let isRefreshing = false;
  let queue: Array<(token: string) => void> = [];

  function flushQueue(newToken: string) {
    queue.forEach((cb) => cb(newToken));
    queue = [];
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
        auth.resetForGuest();
        return Promise.reject(error);
      }
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          queue.push((newToken: string) => {
            original.headers = original.headers ?? {};
            (original.headers as any).Authorization = `Bearer ${newToken}`;
            resolve($api(original));
          });
        });
      }

      isRefreshing = true;

      try {
        const r = await $api.post("/api/iam/refresh");
        const newToken = (r.data as any)?.access_token as string | undefined;

        if (!newToken) {
          auth.resetForGuest();
          isRefreshing = false;
          queue = [];
          return Promise.reject(error);
        }

        auth.setToken(newToken);

        isRefreshing = false;
        flushQueue(newToken);

        original.headers = original.headers ?? {};
        (original.headers as any).Authorization = `Bearer ${newToken}`;
        return $api(original);
      } catch (refreshErr) {
        isRefreshing = false;
        queue = [];
        auth.resetForGuest();
        return Promise.reject(refreshErr);
      }
    }
  );
});
