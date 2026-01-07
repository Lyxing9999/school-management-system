<script setup lang="ts">
definePageMeta({ layout: "default" });

import { computed, onMounted, ref, watch } from "vue";
import { useNuxtApp, useRoute, navigateTo } from "nuxt/app";
import {
  Bell,
  Refresh,
  Check,
  CircleCheck,
  Search,
} from "@element-plus/icons-vue";

import { useMessage } from "~/composables/common/useMessage";
import { useNotificationStore } from "~/stores/notificationStore";
import { storeToRefs } from "pinia";

import BaseButton from "~/components/base/BaseButton.vue";
import NotificationDrawer from "~/components/notifications/NotificationDrawer.vue";

import { NotificationApi } from "~/api/notifications/notification.api";
import type { NotificationDTO } from "~/api/notifications/notification.dto";
import { formatDate } from "~/utils/date/formatDate";

const route = useRoute();
const msg = useMessage();

const notifStore = useNotificationStore();
const { unreadCount } = storeToRefs(notifStore);

const { $api } = useNuxtApp();
const notifApi = new NotificationApi($api as any, "/api");

type FilterMode = "all" | "unread";
const filter = ref<FilterMode>(
  (String(route.query.filter ?? "all") as any) === "unread" ? "unread" : "all"
);
const q = ref<string>(String(route.query.q ?? ""));

const loading = ref(false);
const items = ref<NotificationDTO[]>([]);

const limit = ref<number>(30);

watch(
  () => route.query.filter,
  (v) => {
    const f = String(v ?? "all");
    filter.value = f === "unread" ? "unread" : "all";
  }
);

watch(
  () => route.query.q,
  (v) => {
    q.value = String(v ?? "");
  }
);

function setRouteQuery() {
  navigateTo({
    path: route.path,
    query: {
      ...route.query,
      filter: filter.value,
      q: q.value || undefined,
    },
  });
}

watch([filter, q], () => setRouteQuery());

const visibleItems = computed(() => {
  const base =
    filter.value === "unread"
      ? items.value.filter((x) => !x.read_at)
      : items.value;

  const keyword = q.value.trim().toLowerCase();
  if (!keyword) return base;

  return base.filter((n) => {
    const hay = `${n.title ?? ""} ${n.message ?? ""} ${
      n.type ?? ""
    }`.toLowerCase();
    return hay.includes(keyword);
  });
});

async function refreshUnread() {
  await notifStore.refreshUnread();
}

async function load() {
  loading.value = true;
  try {
    const res = await notifApi.listLatest(limit.value);
    const raw = (res as any)?.data?.items ?? (res as any)?.items ?? [];
    items.value = Array.isArray(raw) ? raw : [];
    await refreshUnread();
  } catch {
    items.value = [];
    msg.showError("Failed to load notifications");
  } finally {
    loading.value = false;
  }
}

async function markRead(n: NotificationDTO) {
  if (!n?.id || n.read_at) return;

  const prev = n.read_at;
  n.read_at = new Date().toISOString(); 

  try {
    await notifApi.markRead(String(n.id));
    await refreshUnread();
  } catch {
    n.read_at = prev ?? null;
    msg.showError("Failed to mark as read");
  }
}

async function markAllRead() {
  if (!items.value.length) return;

  const anyUnread = items.value.some((x) => !x.read_at);
  if (!anyUnread) {
    msg.showSuccess("No unread notifications");
    return;
  }

  // optimistic
  const now = new Date().toISOString();
  const snapshot = items.value.map((x) => ({ id: x.id, read_at: x.read_at }));

  items.value = items.value.map((x) => ({ ...x, read_at: x.read_at || now }));

  try {
    await notifApi.markAllRead();
    await refreshUnread();
    msg.showSuccess("All notifications marked as read");
  } catch {
    // rollback
    const map = new Map(snapshot.map((x) => [String(x.id), x.read_at]));
    items.value = items.value.map((x) => ({
      ...x,
      read_at: map.get(String(x.id)) ?? x.read_at,
    }));
    msg.showError("Failed to mark all as read");
  }
}

function openDrawer() {
  notifStore.toggleDrawer(true);
}

onMounted(async () => {
  await load();
});
</script>

<template>
  <div class="notif-page">
    <div class="notif-container space-y-4">
      <div class="notif-header">
        <div class="flex items-center gap-2">
          <el-icon><Bell /></el-icon>
          <div class="min-w-0">
            <div class="text-lg font-semibold">Notifications</div>
            <div class="text-sm text-[var(--muted-color)]">
              All system messages, alerts, and updates.
            </div>
          </div>
        </div>

        <div class="notif-header__right">
          <el-tag v-if="Number(unreadCount) > 0" type="danger">
            {{ Number(unreadCount) }} unread
          </el-tag>

          <BaseButton plain size="small" @click="openDrawer"
            >Open drawer</BaseButton
          >

          <BaseButton plain size="small" :loading="loading" @click="load">
            <el-icon class="mr-1"><Refresh /></el-icon>
            Refresh
          </BaseButton>

          <BaseButton type="primary" plain size="small" @click="markAllRead">
            <el-icon class="mr-1"><Check /></el-icon>
            Mark all read
          </BaseButton>
        </div>
      </div>

      <el-card class="app-card" shadow="never">
        <div class="filters">
          <el-segmented
            v-model="filter"
            :options="[
              { label: 'All', value: 'all' },
              { label: 'Unread', value: 'unread' },
            ]"
          />

          <el-input
            v-model="q"
            class="search"
            clearable
            placeholder="Search title/message..."
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select v-model="limit" class="limit" @change="load">
            <el-option :label="'30 latest'" :value="30" />
            <el-option :label="'50 latest'" :value="50" />
            <el-option :label="'100 latest'" :value="100" />
          </el-select>
        </div>

        <el-skeleton v-if="loading" :rows="8" animated />

        <el-empty
          v-else-if="!visibleItems.length"
          description="No notifications found."
        />

        <div v-else class="list">
          <el-card
            v-for="n in visibleItems"
            :key="n.id"
            class="row"
            shadow="never"
          >
            <div class="row-inner">
              <div class="min-w-0">
                <div class="row-title">
                  <span class="font-medium truncate">{{ n.title }}</span>
                  <el-tag
                    v-if="!n.read_at"
                    type="danger"
                    size="small"
                    class="ml-2"
                    >Unread</el-tag
                  >
                  <el-tag v-else type="info" size="small" class="ml-2"
                    >Read</el-tag
                  >
                </div>

                <div class="text-sm text-[var(--muted-color)] mt-1">
                  {{ n.message || "—" }}
                </div>

                <div class="text-xs text-[var(--muted-color)] mt-2">
                  {{ formatDate(n.created_at) }}
                  <span v-if="n.read_at">
                    • Read: {{ formatDate(n.read_at) }}</span
                  >
                </div>
              </div>

              <div class="actions">
                <el-button
                  v-if="!n.read_at"
                  size="small"
                  plain
                  @click="markRead(n)"
                >
                  <el-icon class="mr-1"><CircleCheck /></el-icon>
                  Mark read
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-card>

      <NotificationDrawer />
    </div>
  </div>
</template>

<style scoped>
.notif-page {
  padding: 16px;
}

.notif-container {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.notif-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.notif-header__right {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.filters {
  display: grid;
  grid-template-columns: 220px 1fr 160px;
  gap: 10px;
  align-items: center;
}

.search {
  min-width: 0;
}

.limit {
  width: 160px;
  justify-self: end;
}

.list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row {
  border: 1px solid var(--border-color);
}

.row-inner {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: space-between;
}

.row-title {
  display: flex;
  align-items: center;
  min-width: 0;
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .notif-header {
    flex-direction: column;
    align-items: stretch;
  }
  .filters {
    grid-template-columns: 1fr;
  }
  .limit {
    width: 100%;
    justify-self: stretch;
  }
  .actions {
    justify-content: flex-end;
  }
}
</style>
