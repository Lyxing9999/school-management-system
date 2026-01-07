import { defineStore } from "pinia";
import { computed, ref, watch, type WatchStopHandle } from "vue";
import { useCookie } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";

export type InlineEditMode = "auto" | "manual";

export const usePreferencesStore = defineStore("preferences", () => {
  /**
   * Constants
   */
  const ALLOWED_PAGE_SIZES = [10, 20, 50, 100] as const;
  const DEFAULT_TABLE_PAGE_SIZE = 10 as const;
  type AllowedPageSize = (typeof ALLOWED_PAGE_SIZES)[number];

  const authStore = useAuthStore();

  /**
   * Scope per user id (best), fallback role, fallback guest.
   */
  const scopeId = computed(() => {
    const id = authStore.user?.id;
    if (id) return String(id);

    const role = authStore.user?.role;
    if (role) return String(role).toLowerCase();

    return "guest";
  });

  const key = (name: string) => `pref_${name}__${scopeId.value}`;

  function isAllowedPageSize(v: number): v is AllowedPageSize {
    return ALLOWED_PAGE_SIZES.includes(v as any);
  }

  /**
   * Store state (writable refs)
   * These are what your app should use.
   */
  const inlineEditMode = ref<InlineEditMode>("auto");
  const tablePageSize = ref<number>(DEFAULT_TABLE_PAGE_SIZE);
  const notifAutoRefresh = ref<boolean>(true);

  /**
   * Cookie bindings (internal)
   * Re-bind whenever scopeId changes, and sync state <-> cookies.
   */
  let stopSync: WatchStopHandle[] = [];

  function cleanupSync() {
    stopSync.forEach((s) => s());
    stopSync = [];
  }

  function bindScopedCookies() {
    cleanupSync();

    const inlineCookie = useCookie<InlineEditMode>(key("inline_edit_mode"), {
      sameSite: "lax",
      path: "/",
      default: () => "auto",
    });

    const pageSizeCookie = useCookie<number>(key("table_page_size"), {
      sameSite: "lax",
      path: "/",
      default: () => DEFAULT_TABLE_PAGE_SIZE,
    });

    const notifCookie = useCookie<boolean>(key("notif_auto_refresh"), {
      sameSite: "lax",
      path: "/",
      default: () => true,
    });

    // ---- hydrate state from cookies (with validation)
    inlineEditMode.value = (inlineCookie.value ?? "auto") as InlineEditMode;

    const rawSize = Number(pageSizeCookie.value);
    tablePageSize.value = isAllowedPageSize(rawSize)
      ? rawSize
      : DEFAULT_TABLE_PAGE_SIZE;

    notifAutoRefresh.value = Boolean(notifCookie.value);

    // ---- sync state -> cookies
    stopSync.push(
      watch(
        inlineEditMode,
        (v) => {
          inlineCookie.value = v;
        },
        { flush: "sync" }
      )
    );

    stopSync.push(
      watch(
        tablePageSize,
        (v) => {
          const next = Number(v);
          pageSizeCookie.value = isAllowedPageSize(next)
            ? next
            : DEFAULT_TABLE_PAGE_SIZE;
          // ensure local state always valid too
          tablePageSize.value = Number(pageSizeCookie.value);
        },
        { flush: "sync" }
      )
    );

    stopSync.push(
      watch(
        notifAutoRefresh,
        (v) => {
          notifCookie.value = Boolean(v);
        },
        { flush: "sync" }
      )
    );
  }

  // Re-bind when user changes (id/role/guest)
  watch(scopeId, bindScopedCookies, { immediate: true });

  /**
   * Public helpers / actions
   */
  function getTablePageSize(): number {
    const v = Number(tablePageSize.value);
    return isAllowedPageSize(v) ? v : DEFAULT_TABLE_PAGE_SIZE;
  }

  function setTablePageSize(v: number) {
    const next = Number(v);
    tablePageSize.value = isAllowedPageSize(next)
      ? next
      : DEFAULT_TABLE_PAGE_SIZE;
  }

  function resetTablePageSize() {
    tablePageSize.value = DEFAULT_TABLE_PAGE_SIZE;
  }

  function getAllowedPageSizes(): number[] {
    return [...ALLOWED_PAGE_SIZES]; // mutable array for Element Plus
  }

  function setInlineEditMode(v: InlineEditMode) {
    inlineEditMode.value = v;
  }

  function setNotifAutoRefresh(v: boolean) {
    notifAutoRefresh.value = Boolean(v);
  }

  return {
    // state (writable)
    inlineEditMode,
    tablePageSize,
    notifAutoRefresh,

    // constants
    ALLOWED_PAGE_SIZES,
    DEFAULT_TABLE_PAGE_SIZE,

    // helpers
    getAllowedPageSizes,
    getTablePageSize,

    // actions
    setInlineEditMode,
    setTablePageSize,
    resetTablePageSize,
    setNotifAutoRefresh,
  };
});
