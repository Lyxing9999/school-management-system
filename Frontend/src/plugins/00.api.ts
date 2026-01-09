
import axios from "axios";
import type { AxiosInstance } from "axios";

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig();

  const ssrHeaders = import.meta.server
    ? useRequestHeaders(["cookie"])
    : undefined;

  const api: AxiosInstance = axios.create({
    baseURL: config.public.apiBase,
    timeout: 15000,
    withCredentials: true,
    headers: {
      ...(ssrHeaders?.cookie ? { cookie: ssrHeaders.cookie } : {}),
    },
  });

  return { provide: { api } };
});
