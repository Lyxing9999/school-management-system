// ~/plugins/api.ts
import axios, { type AxiosError, type AxiosRequestConfig } from "axios";
import { useRuntimeConfig, navigateTo } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";

type RetryConfig = AxiosRequestConfig & { _retry?: boolean };

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  const authStore = useAuthStore();

  const api = axios.create({
    baseURL: config.public.apiBase,
    timeout: 10000,
    withCredentials: true, // refresh cookie
  });

  // Separate client to avoid interceptor loops
  const refreshApi = axios.create({
    baseURL: config.public.apiBase,
    timeout: 10000,
    withCredentials: true,
  });

  api.interceptors.request.use((cfg) => {
    const token = authStore.token; // Pinia setup-store unwraps refs
    if (token) {
      cfg.headers = cfg.headers ?? {};
      cfg.headers.Authorization = `Bearer ${token}`;
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

      // Network / CORS / no response
      if (!error.response) return Promise.reject(error);

      const status = error.response.status;
      const url = String(original.url || "");

      const isAuthRoute =
        url.includes("/api/iam/login") || url.includes("/api/iam/refresh");
      if (status !== 401 || isAuthRoute) return Promise.reject(error);

      // Already retried once => force logout
      if (original._retry) {
        authStore.clear();
        await navigateTo("/auth/login");
        return Promise.reject(error);
      }
      original._retry = true;

      // Queue while refresh in-flight
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
          authStore.clear();
          await navigateTo("/auth/login");
          return Promise.reject(error);
        }

        authStore.setToken(newToken);

        isRefreshing = false;
        flushQueue(newToken);

        original.headers = original.headers ?? {};
        (original.headers as any).Authorization = `Bearer ${newToken}`;
        return api(original);
      } catch (refreshErr) {
        isRefreshing = false;
        queue = [];

        authStore.clear();
        await navigateTo("/auth/login");
        return Promise.reject(refreshErr);
      }
    }
  );

  return { provide: { api } };
});
