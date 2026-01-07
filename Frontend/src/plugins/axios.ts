import axios, { type AxiosError, type AxiosRequestConfig } from "axios";
import { useRuntimeConfig } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";

type RetryConfig = AxiosRequestConfig & { _retry?: boolean };

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  const auth = useAuthStore();

  const api = axios.create({
    baseURL: config.public.apiBase,
    timeout: 10000,
    withCredentials: true,
  });

  const refreshApi = axios.create({
    baseURL: config.public.apiBase,
    timeout: 10000,
    withCredentials: true,
  });

  api.interceptors.request.use((cfg) => {
    if (auth.token) {
      cfg.headers = cfg.headers ?? {};
      (cfg.headers as any).Authorization = `Bearer ${auth.token}`;
    }
    return cfg;
  });

  let isRefreshing = false;
  let queue: Array<(token: string) => void> = [];

  function flushQueue(newToken: string) {
    queue.forEach((cb) => cb(newToken));
    queue = [];
  }

  api.interceptors.response.use(
    (res) => res,
    async (error: AxiosError) => {
      const original = (error.config || {}) as RetryConfig;
      if (!error.response) return Promise.reject(error);

      const status = error.response.status;
      const url = String(original.url || "");
      const isAuthRoute =
        url.includes("/api/iam/login") || url.includes("/api/iam/refresh");

      if (status !== 401 || isAuthRoute) return Promise.reject(error);

      if (original._retry) {
        // do NOT navigate here; let middleware handle redirect
        auth.resetForGuest();
        return Promise.reject(error);
      }
      original._retry = true;

      if (isRefreshing) {
        return new Promise((resolve) => {
          queue.push((newToken: string) => {
            original.headers = original.headers ?? {};
            (original.headers as any).Authorization = `Bearer ${newToken}`;
            resolve(api(original));
          });
        });
      }

      isRefreshing = true;

      try {
        const r = await refreshApi.post("/api/iam/refresh");
        const newToken = (r.data as any)?.access_token as string | undefined;

        if (!newToken) {
          auth.resetForGuest();
          return Promise.reject(error);
        }

        auth.setToken(newToken);
        isRefreshing = false;
        flushQueue(newToken);

        original.headers = original.headers ?? {};
        (original.headers as any).Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch (refreshErr) {
        isRefreshing = false;
        queue = [];
        auth.resetForGuest();
        return Promise.reject(refreshErr);
      }
    }
  );

  return { provide: { api } };
});
