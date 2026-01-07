import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { NotificationDTO } from "~/api/notifications/notification.dto";
import { NotificationApi } from "~/api/notifications/notification.api";
import type { AxiosInstance } from "axios";

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

  async function refreshUnread() {
    const api = getApi();
    const res = (await api.unreadCount()) as Wrapped<{ unread: number }>;
    unread.value = Number(res?.data?.unread ?? 0);
  }

  async function loadLatest(limit = 30) {
    const api = getApi();
    const res = (await api.listLatest(limit)) as Wrapped<{
      items: NotificationDTO[];
    }>;
    items.value = Array.isArray(res?.data?.items) ? res.data.items : [];
    await refreshUnread();
  }

  // keep badge robust even if you miss some events
  let refreshTimer: any = null;
  function refreshUnreadSoon(delayMs = 250) {
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => refreshUnread(), delayMs);
  }

  function has(id: string) {
    return items.value.some((x) => String(x.id) === String(id));
  }

  function pushRealtime(n: NotificationDTO) {
    if (!n?.id) return;

    // dedupe (important in prod, socket reconnect can replay)
    if (has(String(n.id))) {
      refreshUnreadSoon(200);
      return;
    }

    items.value = [n, ...items.value].slice(0, 50);

    if (!n.read_at) unread.value = unread.value + 1;
    refreshUnreadSoon(300);
  }

  async function markRead(id: string) {
    const api = getApi();

    // optimistic
    const idx = items.value.findIndex((x) => String(x.id) === String(id));
    if (idx >= 0 && !items.value[idx].read_at) {
      items.value[idx] = {
        ...items.value[idx],
        read_at: new Date().toISOString(),
      };
      unread.value = Math.max(0, unread.value - 1);
    }

    await api.markRead(id);
    await refreshUnread();
  }

  async function markAllRead() {
    const api = getApi();

    const now = new Date().toISOString();
    items.value = items.value.map((x) =>
      x.read_at ? x : { ...x, read_at: now }
    );
    unread.value = 0;

    await api.markAllRead();
    await refreshUnread();
  }

  return {
    items,
    unread,
    drawerOpen,
    unreadCount,
    latest,

    toggleDrawer,
    refreshUnread,
    loadLatest,
    pushRealtime,
    markRead,
    markAllRead,
  };
});
