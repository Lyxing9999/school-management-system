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

import { NOTIF_TYPE_OPTIONS } from "~/utils/constants/notification";
import type { NotifType } from "~/api/notifications/notification.dto";

import { formatDate } from "~/utils/date/formatDate";

const route = useRoute();
const msg = useMessage();

const notif = useNotificationStore();
const { unreadCount } = storeToRefs(notif);

type FilterMode = "all" | "unread";
const filter = ref<FilterMode>(
  String(route.query.filter ?? "all") === "unread" ? "unread" : "all"
);

type TypeFilter = "all" | NotifType;
const typeFilter = ref<TypeFilter>(String(route.query.type ?? "all") as any);

// keep q local so typing doesn't cause router navigation
const q = ref<string>(String(route.query.q ?? ""));

const limit = ref<number>(Number(route.query.limit ?? 30) || 30);

const loading = ref(false);
const items = ref<NotificationDTO[]>([]);

function normalizeQuery(obj: Record<string, any>) {
  const out: Record<string, string> = {};
  Object.entries(obj).forEach(([k, v]) => {
    if (v === undefined || v === null || v === "") return;
    out[k] = String(v);
  });
  return out;
}

function sameQuery(a: Record<string, any>, b: Record<string, any>) {
  const aa = normalizeQuery(a);
  const bb = normalizeQuery(b);

  const ka = Object.keys(aa).sort();
  const kb = Object.keys(bb).sort();
  if (ka.length !== kb.length) return false;

  for (let i = 0; i < ka.length; i++) {
    const k = ka[i];
    if (k !== kb[i]) return false;
    if (aa[k] !== bb[k]) return false;
  }
  return true;
}

// Sync query -> state (filter/type/limit only; q stays local)
watch(
  () => route.query.filter,
  (v) => (filter.value = String(v ?? "all") === "unread" ? "unread" : "all")
);

watch(
  () => route.query.type,
  (v) => {
    const t = String(v ?? "all");
    const allowed = new Set(["all", ...NOTIF_TYPE_OPTIONS.map((x) => x.value)]);
    typeFilter.value = allowed.has(t) ? (t as TypeFilter) : "all";
  }
);

watch(
  () => route.query.limit,
  (v) => {
    const n = Number(v ?? 30);
    limit.value = [30, 50, 100].includes(n) ? n : 30;
  }
);

// Write state -> query (NO q to avoid typing lag)
function setRouteQuery(replace = true) {
  const nextQuery = {
    ...route.query,
    filter: filter.value,
    type: typeFilter.value !== "all" ? String(typeFilter.value) : undefined,
    limit: limit.value !== 30 ? String(limit.value) : undefined,
  };

  if (sameQuery(route.query as any, nextQuery as any)) return;

  navigateTo({ path: route.path, query: nextQuery }, { replace });
}

// Only sync non-typing controls
watch([filter, typeFilter, limit], () => setRouteQuery(true));

// Visible list (client-side)
const visibleItems = computed(() => {
  let base =
    filter.value === "unread"
      ? items.value.filter((x) => !x.read_at)
      : items.value;

  if (typeFilter.value !== "all") {
    base = base.filter((x) => x.type === typeFilter.value);
  }

  const keyword = q.value.trim().toLowerCase();
  if (!keyword) return base;

  return base.filter((n) => {
    const hay = `${n.title ?? ""} ${n.message ?? ""} ${
      n.type ?? ""
    }`.toLowerCase();
    return hay.includes(keyword);
  });
});

const canReset = computed(() => {
  return (
    filter.value !== "all" ||
    typeFilter.value !== "all" ||
    q.value.trim() !== "" ||
    limit.value !== 30
  );
});

function resetFilters() {
  filter.value = "all";
  typeFilter.value = "all";
  q.value = "";
  limit.value = 30;

  setRouteQuery(true);
  load();
}

function openDrawer() {
  notif.toggleDrawer(true);
}

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

  const prev = n.read_at;
  n.read_at = new Date().toISOString(); // optimistic local

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

async function openNotification(n: NotificationDTO) {
  if (!n.read_at) await markRead(n);

  const r = (n.data as any)?.route;
  if (r) navigateTo({ path: String(r) });
}

onMounted(async () => {
  await load();
});
</script>
<template>
  <div class="notif-page">
    <div class="notif-container space-y-4">
      <!-- Header -->
      <div class="notif-header">
        <div class="flex items-center gap-2 min-w-0">
          <el-icon><Bell /></el-icon>

          <div class="min-w-0">
            <div class="text-lg font-semibold">Teacher Notifications</div>
            <div class="text-sm text-[var(--muted-color)]">
              Class updates, enrollments, schedule changes, and system alerts.
            </div>
          </div>
        </div>

        <div class="notif-actions">
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

      <!-- Card -->
      <el-card class="app-card" shadow="never">
        <!-- Filters -->
        <el-row :gutter="10" align="middle" class="filters-row">
          <el-col :xs="24" :sm="12" :md="6" :lg="5">
            <el-segmented
              class="base-segmented w-full"
              v-model="filter"
              :options="[
                { label: 'All', value: 'all' },
                { label: 'Unread', value: 'unread' },
              ]"
            />
          </el-col>

          <el-col :xs="24" :sm="12" :md="10" :lg="8">
            <el-input
              v-model="q"
              class="w-full"
              clearable
              placeholder="Search..."
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-select v-model="typeFilter" class="w-full" placeholder="Type">
              <el-option label="All types" value="all" />
              <el-option
                v-for="t in NOTIF_TYPE_OPTIONS"
                :key="t.value"
                :label="t.label"
                :value="t.value"
              />
            </el-select>
          </el-col>

          <el-col :xs="24" :sm="12" :md="6" :lg="3">
            <el-select v-model="limit" class="w-full" @change="load">
              <el-option label="30 latest" :value="30" />
              <el-option label="50 latest" :value="50" />
              <el-option label="100 latest" :value="100" />
            </el-select>
          </el-col>

          <el-col :xs="24" :sm="12" :md="4" :lg="2">
            <el-button
              plain
              class="w-full"
              :disabled="!canReset"
              @click="resetFilters"
            >
              Reset
            </el-button>
          </el-col>
        </el-row>

        <el-divider class="my-4" />

        <!-- Body -->
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
                  <span class="meta-time">{{ formatDate(n.created_at) }}</span>
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

/* header */
.notif-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.notif-actions {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* filters row */
.filters-row :deep(.el-col) {
  min-width: 0; /* critical so inputs/selects shrink */
}

/* list */
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.row {
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color var(--transition-base);
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

/* mobile: keep actions below title, keep card rows readable */
@media (max-width: 768px) {
  .notif-header {
    flex-direction: column;
    align-items: stretch;
  }
  .notif-actions {
    justify-content: flex-end;
  }
  .row-inner {
    flex-direction: column;
    align-items: stretch;
  }
  .actions {
    display: flex;
    justify-content: flex-end;
  }
}
</style>
