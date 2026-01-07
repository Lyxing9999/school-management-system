<script setup lang="ts">
import { computed, watch } from "vue";
import { storeToRefs } from "pinia";
import { useNotificationStore } from "~/stores/notificationStore";
import { navigateTo } from "nuxt/app";
import { formatDate } from "~/utils/date/formatDate";
import type { NotificationDTO } from "~/api/notifications/notification.dto";

const notif = useNotificationStore();
const { drawerOpen, latest, unreadCount } = storeToRefs(notif);

// always an array (prevents items.length crash if latest is null/undefined)
const items = computed<NotificationDTO[]>(() => latest.value ?? []);

watch(
  () => drawerOpen.value,
  async (open) => {
    if (!open) return;
    await notif.loadLatest(30);
  }
);

const close = () => notif.toggleDrawer(false);

async function openItem(n: NotificationDTO) {
  if (!n?.id) return;

  // mark read first (optimistic handled in store)
  if (!n.read_at) {
    await notif.markRead(String(n.id));
  }

  // navigate without query params (route should be a plain path)
  const r = n?.data?.route;
  if (r) navigateTo({ path: String(r) });
}
</script>

<template>
  <el-drawer
    v-model="drawerOpen"
    title="Notifications"
    direction="rtl"
    size="360px"
    :with-header="true"
    @close="close"
  >
    <div class="flex items-center justify-between mb-3">
      <div class="text-sm text-[var(--muted-color)]">
        Unread: <span class="font-semibold">{{ unreadCount }}</span>
      </div>

      <el-button
        size="small"
        :disabled="unreadCount === 0"
        @click="notif.markAllRead()"
      >
        Mark all read
      </el-button>
    </div>

    <div
      v-if="items.length > 0 && unreadCount === 0"
      class="text-sm text-[var(--muted-color)] mb-2"
    >
      No unread notifications.
    </div>

    <el-empty v-if="items.length === 0" description="No notifications yet." />

    <div v-else class="space-y-2">
      <el-card
        v-for="n in items"
        :key="n.id"
        class="cursor-pointer"
        shadow="never"
        @click="openItem(n)"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <div class="font-medium truncate">
              {{ n.title }}
            </div>

            <div
              v-if="n.message"
              class="text-sm text-[var(--muted-color)] mt-1"
            >
              {{ n.message }}
            </div>

            <div class="text-xs text-[var(--muted-color)] mt-2">
              {{ formatDate(n.created_at) }}
            </div>

            <div
              v-if="n.read_at"
              class="text-xs text-[var(--muted-color)] mt-1"
            >
              Read: {{ formatDate(n.read_at) }}
            </div>
          </div>

          <el-tag v-if="!n.read_at" type="danger" size="small">New</el-tag>
          <el-tag v-else type="info" size="small">Read</el-tag>
        </div>
      </el-card>
    </div>
  </el-drawer>
</template>
