import { defineStore } from "pinia";
import { ref, computed, onScopeDispose } from "vue";
import { useNuxtApp } from "nuxt/app";
import type { AxiosInstance } from "axios";

import type { NotificationDTO } from "~/api/notifications/notification.dto";
import { NotificationApi } from "~/api/notifications/notification.api";

type Wrapped<T> = {
  success: boolean;
  message?: string;
  data: T;
};

export const useNotificationStore = defineStore("notification", () => {
  const items = ref<NotificationDTO[]>([]);
  const unread = ref<number>(0);
  const drawerOpen = ref(false);

  const unreadCount = computed(() => unread.value);
  const latest = computed(() => items.value);

  function toggleDrawer(v?: boolean) {
    drawerOpen.value = typeof v === "boolean" ? v : !drawerOpen.value;
  }

  function getApi() {
    const { $api } = useNuxtApp();
    return new NotificationApi($api as AxiosInstance);
  }

  async function refreshUnread(): Promise<number> {
    try {
      const api = getApi();
      const res = (await api.unreadCount()) as Wrapped<{ unread: number }>;
      const n = Number(res?.data?.unread ?? 0);
      unread.value = Number.isFinite(n) ? n : 0;
      return unread.value;
    } catch {
      // Keep UI stable even if API fails
      return unread.value;
    }
  }

  async function loadLatest(limit = 30): Promise<NotificationDTO[]> {
    try {
      const api = getApi();

      // IMPORTANT: pass object, not number
      const res = (await api.listLatest({ limit })) as Wrapped<{
        items: NotificationDTO[];
      }>;

      const list = Array.isArray(res?.data?.items) ? res.data.items : [];
      items.value = list;

      await refreshUnread();
      return items.value;
    } catch {
      await refreshUnread();
      return items.value;
    }
  }

  function has(id: string) {
    return items.value.some((x) => String(x.id) === String(id));
  }

  // Debounced refresh (robust badge even if socket events are missed)
  let refreshTimer: ReturnType<typeof setTimeout> | null = null;

  function refreshUnreadSoon(delayMs = 250) {
    if (refreshTimer) clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => {
      refreshTimer = null;
      void refreshUnread();
    }, delayMs);
  }

  function pushRealtime(n: NotificationDTO) {
    if (!n?.id) return;

    const nid = String(n.id);

    // Deduplicate (socket reconnect can replay)
    if (has(nid)) {
      refreshUnreadSoon(200);
      return;
    }

    items.value = [n, ...items.value].slice(0, 50);

    // Optimistic unread increment
    if (!n.read_at) unread.value = unread.value + 1;

    refreshUnreadSoon(300);
  }

  async function markRead(id: string) {
    const api = getApi();
    const sid = String(id);

    // optimistic UI
    const idx = items.value.findIndex((x) => String(x.id) === sid);
    if (idx >= 0 && !items.value[idx].read_at) {
      items.value[idx] = {
        ...items.value[idx],
        read_at: new Date().toISOString(),
      };
      unread.value = Math.max(0, unread.value - 1);
    }

    try {
      await api.markRead(sid);
    } finally {
      await refreshUnread();
    }
  }

  async function markAllRead() {
    const api = getApi();

    // optimistic UI
    const now = new Date().toISOString();
    items.value = items.value.map((x) =>
      x.read_at ? x : { ...x, read_at: now }
    );
    unread.value = 0;

    try {
      await api.markAllRead();
    } finally {
      await refreshUnread();
    }
  }

  // Cleanup timers when the store scope is disposed (HMR / navigation)
  onScopeDispose(() => {
    if (refreshTimer) clearTimeout(refreshTimer);
    refreshTimer = null;
  });

  return {
    items,
    unread,
    drawerOpen,
    unreadCount,
    latest,

    toggleDrawer,
    refreshUnread,
    refreshUnreadSoon,
    loadLatest,
    pushRealtime,
    markRead,
    markAllRead,
  };
});
