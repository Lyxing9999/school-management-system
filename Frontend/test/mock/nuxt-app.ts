import { vi } from "vitest";

export const useRouter = vi.fn(() => ({
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  currentRoute: {
    value: {
      params: {},
      query: {},
      path: "/",
    },
  },
}));

export const useRoute = vi.fn(() => ({
  params: {},
  query: {},
  path: "/",
  name: "index",
  meta: {},
}));

export const useRuntimeConfig = vi.fn(() => ({
  public: {},
  app: {
    baseURL: "/",
    buildAssetsDir: "/_nuxt/",
    cdnURL: "",
  },
}));

export const navigateTo = vi.fn();
export const abortNavigation = vi.fn();
export const setPageLayout = vi.fn();
export const definePageMeta = vi.fn();

export default {
  useRouter,
  useRoute,
  useRuntimeConfig,
  navigateTo,
  abortNavigation,
  setPageLayout,
  definePageMeta,
};
