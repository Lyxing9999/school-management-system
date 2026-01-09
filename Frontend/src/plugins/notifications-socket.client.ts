import { io, type Socket } from "socket.io-client";
import { watch } from "vue";
import { useAuthStore } from "~/stores/authStore";
import { useNotificationStore } from "~/stores/notificationStore";

type GlobalSocketState = {
  socket: Socket | null;
  token: string | null;
};

export default defineNuxtPlugin(() => {
  if (!import.meta.client) return;

  const auth = useAuthStore();
  const notif = useNotificationStore();

  // IMPORTANT: must be your backend origin in production
  const baseURL = useRuntimeConfig().public.apiBase;

  const g = globalThis as any;
  const state: GlobalSocketState =
    g.__notif_socket_state__ ??
    (g.__notif_socket_state__ = { socket: null, token: null });

  const isDev = import.meta.dev;

  const disconnect = () => {
    if (!state.socket) return;
    state.socket.removeAllListeners();
    state.socket.disconnect();
    state.socket = null;
    state.token = null;
  };

  const connect = (token: string) => {
    if (state.socket && state.token === token && state.socket.connected) return;

    disconnect();
    state.token = token;

    const socket = io(baseURL, {
      path: "/socket.io",
      transports: ["websocket", "polling"],
      withCredentials: true,
      query: { token },
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 500,
      reconnectionDelayMax: 5000,
      timeout: 20000,
    });

    state.socket = socket;

    if (isDev) {
      socket.onAny((event, payload) => {
        console.log("[socket:any]", event, payload);
      });
    }

    socket.on("connect", async () => {
      if (isDev) console.log("[socket] connected", socket.id);
      await notif.refreshUnread();
    });

    socket.on("notification:new", (payload: any) => {
      if (isDev) console.log("[socket] notification:new", payload);
      notif.pushRealtime(payload);
    });

    socket.on("connect_error", (err: any) => {
      if (isDev) console.log("[socket] connect_error", err?.message ?? err);
    });

    socket.on("disconnect", (reason) => {
      if (isDev) console.log("[socket] disconnected", reason);
    });
  };

  if (auth.token) connect(auth.token);

  watch(
    () => auth.token,
    (token) => {
      if (token) connect(token);
      else disconnect();
    }
  );

  window.addEventListener("online", () => {
    if (auth.token) connect(auth.token);
  });
});
