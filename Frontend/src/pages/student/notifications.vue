<script setup lang="ts">
definePageMeta({ layout: "default" });

import { computed, onMounted, ref, watch } from "vue";
import { useRoute, navigateTo } from "nuxt/app";
import { storeToRefs } from "pinia";
import {
  Bell,
  Refresh,
  Check,
  CircleCheck,
  Search,
} from "@element-plus/icons-vue";
import { ElMessageBox } from "element-plus";

import BaseButton from "~/components/base/BaseButton.vue";
import NotificationDrawer from "~/components/notifications/NotificationDrawer.vue";

import { useMessage } from "~/composables/common/useMessage";
import { useNotificationStore } from "~/stores/notificationStore";
import type { NotificationDTO } from "~/api/notifications/notification.dto";

import { formatDate } from "~/utils/date/formatDate";

const route = useRoute();
const msg = useMessage();

const notif = useNotificationStore();
const { unreadCount } = storeToRefs(notif);

type FilterMode = "all" | "unread";

/* -----------------------------
   State (sync with query)
----------------------------- */
const filter = ref<FilterMode>(
  String(route.query.filter ?? "all") === "unread" ? "unread" : "all"
);
const q = ref<string>(String(route.query.q ?? ""));
const limit = ref<number>(Number(route.query.limit ?? 30) || 30);

const loading = ref(false);
const items = ref<NotificationDTO[]>([]);

/* -----------------------------
   Query -> State
----------------------------- */
watch(
  () => route.query.filter,
  (v) => (filter.value = String(v ?? "all") === "unread" ? "unread" : "all")
);
watch(
  () => route.query.q,
  (v) => (q.value = String(v ?? ""))
);
watch(
  () => route.query.limit,
  (v) => {
    const n = Number(v ?? 30);
    limit.value = [30, 50, 100].includes(n) ? n : 30;
  }
);

/* -----------------------------
   State -> Query
----------------------------- */
function setRouteQuery() {
  navigateTo({
    path: route.path,
    query: {
      ...route.query,
      filter: filter.value,
      q: q.value || undefined,
      limit: limit.value !== 30 ? String(limit.value) : undefined,
    },
  });
}
watch([filter, q], () => setRouteQuery());

/* -----------------------------
   UI computed list
----------------------------- */
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

/* -----------------------------
   Helpers
----------------------------- */
function openDrawer() {
  notif.toggleDrawer(true);
}

/* -----------------------------
   Data actions (store-driven)
----------------------------- */
async function load() {
  loading.value = true;
  try {
    await notif.loadLatest(limit.value);
    items.value = [...notif.latest];
  } catch {
    items.value = [];
    msg.showError("Failed to load notifications");
  } finally {
    loading.value = false;
  }
}

async function markRead(n: NotificationDTO) {
  if (!n?.id || n.read_at) return;

  // optimistic local
  const prev = n.read_at;
  n.read_at = new Date().toISOString();

  try {
    await notif.markRead(String(n.id));
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

  try {
    await ElMessageBox.confirm("Mark all notifications as read?", "Confirm", {
      type: "warning",
      confirmButtonText: "Yes",
      cancelButtonText: "No",
    });
  } catch {
    return;
  }

  // optimistic local
  const now = new Date().toISOString();
  items.value = items.value.map((x) =>
    x.read_at ? x : { ...x, read_at: now }
  );

  try {
    await notif.markAllRead();
    msg.showSuccess("All notifications marked as read");
  } catch {
    msg.showError("Failed to mark all as read");
    await load(); // rollback from server
  }
}

/* -----------------------------
   Click row: open notification
----------------------------- */
async function openNotification(n: NotificationDTO) {
  // 1) mark read if unread
  if (!n.read_at) await markRead(n);

  // 2) navigate if route exists
  const r = (n.data as any)?.route;
  if (r) {
    navigateTo(String(r));
    return;
  }

  // fallback: do nothing (still allowed: it becomes read)
}

onMounted(async () => {
  await load();
});
</script>

<template>
  <div class="notif-page">
    <div class="notif-container space-y-4">
      <div class="notif-header">
        <div class="flex items-center gap-2 min-w-0">
          <el-icon><Bell /></el-icon>
          <div class="min-w-0">
            <div class="text-lg font-semibold">Student Notifications</div>
            <div class="text-sm text-[var(--muted-color)]">
              Announcements, grades, attendance, schedule updates, and system
              alerts.
            </div>
          </div>
        </div>

        <div class="notif-header__right">
          <el-tag v-if="Number(unreadCount) > 0" type="danger">
            {{ Number(unreadCount) }} unread
          </el-tag>

          <BaseButton plain size="small" @click="openDrawer">
            Open drawer
          </BaseButton>

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
            placeholder="Search..."
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
            @click="openNotification(n)"
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
                  >
                    Unread
                  </el-tag>

                  <el-tag v-else type="info" size="small" class="ml-2">
                    Read
                  </el-tag>
                </div>

                <div class="text-sm text-[var(--muted-color)] mt-1">
                  {{ n.message || "—" }}
                </div>

                <div class="meta">
                  <span class="meta-chip">{{ n.type }}</span>
                  <span class="meta-dot">•</span>
                  <div class="text-xs text-[var(--muted-color)] mt-2">
                    {{ formatDate(n.created_at) }}
                    <span v-if="n.read_at">
                      • Read: {{ formatDate(n.read_at) }}</span
                    >
                  </div>
                </div>
              </div>

              <div class="actions">
                <el-button
                  v-if="!n.read_at"
                  size="small"
                  plain
                  @click.stop="markRead(n)"
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
  cursor: pointer;
  transition: background 120ms ease;
}

.row:hover {
  background: color-mix(in srgb, var(--hover-bg) 65%, transparent);
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

.meta {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--muted-color);
}

.meta-chip {
  padding: 2px 8px;
  border-radius: 9999px;
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--hover-bg) 55%, transparent);
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-dot {
  opacity: 0.7;
}

.meta-time {
  white-space: nowrap;
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
  .row-inner {
    flex-direction: column;
    align-items: stretch;
  }
  .actions {
    justify-content: flex-end;
  }
}
</style>
