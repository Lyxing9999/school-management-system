// ~/plugins/axios.ts
import axios, { type AxiosError, type AxiosRequestConfig } from "axios";
import { useRuntimeConfig } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";
import { ElMessage } from "element-plus";

type RetryConfig = AxiosRequestConfig & { _retry?: boolean };

function isNetworkError(err: AxiosError) {
  // Axios: no response => network/CORS/DNS/down/timeout
  return !err.response;
}

function isTimeoutError(err: AxiosError) {
  return (
    err.code === "ECONNABORTED" ||
    String(err.message || "")
      .toLowerCase()
      .includes("timeout")
  );
}

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();
  const auth = useAuthStore();

  const baseURL = config.public.apiBase;
  if (!baseURL) {
    console.warn("[api] Missing runtimeConfig.public.apiBase");
  }

  const api = axios.create({
    baseURL,
    timeout: 10000,
    withCredentials: true,
  });

  const refreshApi = axios.create({
    baseURL,
    timeout: 10000,
    withCredentials: true,
  });

  let lastToastAt = 0;
  const toastOnce = (msg: string) => {
    const now = Date.now();
    if (now - lastToastAt < 3000) return;
    lastToastAt = now;
    ElMessage.error(msg);
  };

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

      if (isNetworkError(error)) {
        if (typeof navigator !== "undefined" && navigator.onLine === false) {
          toastOnce("You are offline. Please check your internet connection.");
        } else if (isTimeoutError(error)) {
          toastOnce("Request timed out. Please try again.");
        } else {
          // This covers: backend down, DNS fail, CORS blocked, etc.
          toastOnce("Server is unreachable. Please try again later.");
        }
        return Promise.reject(error);
      }

      const status = error.response?.status;
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
        return new Promise((resolve, reject) => {
          queue.push((newToken: string) => {
            try {
              original.headers = original.headers ?? {};
              (original.headers as any).Authorization = `Bearer ${newToken}`;
              resolve(api(original));
            } catch (e) {
              reject(e);
            }
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
      } catch (refreshErr: any) {
        isRefreshing = false;
        queue = [];

        const axErr = refreshErr as AxiosError;
        if (axErr && !axErr.response) {
          toastOnce("Server is unreachable. Please try again later.");
          return Promise.reject(refreshErr);
        }

        auth.resetForGuest();
        return Promise.reject(refreshErr);
      }
    }
  );

  return { provide: { api } };
});
