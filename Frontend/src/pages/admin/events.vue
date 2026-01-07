<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import debounce from "lodash-es/debounce";
import { ElMessage } from "element-plus";
import type { AxiosError } from "axios";

/* -------------------- Page Meta -------------------- */
definePageMeta({ layout: "default" });

/* -------------------- Base UI -------------------- */
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";

/* -------------------- Composables -------------------- */
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { useHeaderState } from "~/composables/ui/useHeaderState";

/* -------------------- Services -------------------- */
import { adminService } from "~/api/admin";

/**
 * You should implement something like:
 *
 * adminApi.systemEvents.getSystemEventPage(
 *   params: {
 *     q?: string;
 *     eventTypes?: string[];
 *     entityType?: string | null;
 *     from?: string | null; // ISO
 *     to?: string | null;   // ISO
 *     page: number;
 *     pageSize: number;
 *   },
 *   signal?: AbortSignal
 * ): Promise<{ items: SystemEvent[]; total: number }>
 */

/* -------------------- Types -------------------- */
type EntityType =
  | "user"
  | "student"
  | "teacher"
  | "class"
  | "subject"
  | "schedule"
  | "attendance"
  | "grade"
  | "unknown";

type SystemEvent = {
  id: string;
  event: string; // e.g. "STUDENT_CREATED", "CLASS_JOINED"
  entity_type: EntityType;
  entity_id?: string | null;
  actor_id?: string | null;
  actor_display_name?: string | null;
  source?: string | null;
  at: string; // ISO datetime
  meta?: Record<string, any>;
};

/* -------------------- State (filters) -------------------- */
const q = ref("");
const selectedEventTypes = ref<string[]>([]);
const entityType = ref<EntityType | "all">("all");

// Element Plus date-range picker model: [start, end]
const dateRange = ref<[Date | null, Date | null]>([null, null]);

/* -------------------- Helpers -------------------- */
function toIsoOrNull(d: Date | null) {
  return d ? d.toISOString() : null;
}

/**
 * Cancel / Abort errors should not show notifications.
 * - Axios AbortController => often ERR_CANCELED / CanceledError
 */
function isCanceledError(err: any) {
  const axiosErr = err as AxiosError<any>;
  return (
    err?.name === "AbortError" ||
    axiosErr?.code === "ERR_CANCELED" ||
    (typeof err?.message === "string" &&
      err.message.toLowerCase().includes("canceled"))
  );
}

function prettyJson(v: any) {
  try {
    return JSON.stringify(v, null, 2);
  } catch {
    return String(v);
  }
}

/* -------------------- Options -------------------- */
const entityTypeOptions: Array<{ label: string; value: EntityType | "all" }> = [
  { label: "All", value: "all" },
  { label: "User", value: "user" },
  { label: "Student", value: "student" },
  { label: "Teacher", value: "teacher" },
  { label: "Class", value: "class" },
  { label: "Subject", value: "subject" },
  { label: "Schedule", value: "schedule" },
  { label: "Attendance", value: "attendance" },
  { label: "Grade", value: "grade" },
];

/**
 * You can expand this list anytime.
 * Also: you can load event types dynamically from backend later.
 */
const eventTypeOptions = ref<Array<{ label: string; value: string }>>([
  { label: "Student Created", value: "STUDENT_CREATED" },
  { label: "Student Updated", value: "STUDENT_UPDATED" },
  { label: "Class Joined", value: "CLASS_JOINED" },
  { label: "Class Left", value: "CLASS_LEFT" },
  { label: "User Created", value: "USER_CREATED" },
  { label: "User Updated", value: "USER_UPDATED" },
  { label: "User Soft Deleted", value: "USER_SOFT_DELETED" },
  { label: "User Restored", value: "USER_RESTORED" },
  { label: "User Status Changed", value: "USER_STATUS_CHANGED" },
]);

/* -------------------- API -------------------- */
const adminApi = adminService();

/* -------------------- Derived filters for usePaginatedFetch -------------------- */
const filters = computed(() => {
  const [from, to] = dateRange.value;

  return {
    q: q.value.trim(),
    eventTypes: selectedEventTypes.value,
    entityType: entityType.value === "all" ? null : entityType.value,
    from: toIsoOrNull(from),
    to: toIsoOrNull(to),
  };
});

const fetchEvents = async (
  filter: {
    q: string;
    eventTypes: string[];
    entityType: EntityType | null;
    from: string | null;
    to: string | null;
  },
  page: number,
  pageSize: number,
  signal?: AbortSignal
) => {
  // IMPORTANT: your axios request must pass `signal` to support abort
  // Example: axios.get(url, { params, signal })

  const res = await adminApi.systemEvents.getSystemEventPage(
    {
      q: filter.q || undefined,
      eventTypes: filter.eventTypes?.length ? filter.eventTypes : undefined,
      entityType: filter.entityType ?? undefined,
      from: filter.from ?? undefined,
      to: filter.to ?? undefined,
      page,
      pageSize,
    },
    signal
  );

  // expected: { items, total }
  return { items: res.items as SystemEvent[], total: res.total ?? 0 };
};

/* -------------------- Pagination Composable -------------------- */
const {
  data: events,
  loading,
  error,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
  setPageSize,
} = usePaginatedFetch<SystemEvent, typeof filters.value>(
  fetchEvents,
  1,
  20,
  filters
);

/* -------------------- UI: Drawer -------------------- */
const drawerOpen = ref(false);
const activeEvent = ref<SystemEvent | null>(null);

function openEvent(row: SystemEvent) {
  activeEvent.value = row;
  drawerOpen.value = true;
}

function closeDrawer() {
  drawerOpen.value = false;
  activeEvent.value = null;
}

/* -------------------- Watchers -------------------- */
const debouncedFetch = debounce(() => fetchPage(1), 350);

// Filters (except search): fetch immediately
watch(
  [selectedEventTypes, entityType, dateRange],
  async () => {
    debouncedFetch.cancel();
    await fetchPage(1);
  },
  { deep: true }
);

// Search: debounce
watch(
  () => q.value,
  () => debouncedFetch()
);

onBeforeUnmount(() => debouncedFetch.cancel());

/* -------------------- Error handling (optional UI message) -------------------- */
watch(
  () => error.value,
  (e) => {
    if (!e) return;
    if (isCanceledError(e)) return; // ignore cancel
    ElMessage.error(e.message || "Failed to load system events.");
  }
);

/* -------------------- Header stats -------------------- */
const totalEvents = computed(() => totalRows.value ?? 0);

const { headerState } = useHeaderState({
  items: [
    {
      key: "events",
      getValue: () => totalEvents.value,
      singular: "event",
      plural: "events",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "filters",
      getValue: () => {
        const f = filters.value;
        let count = 0;
        if (f.q) count++;
        if (f.eventTypes?.length) count++;
        if (f.entityType) count++;
        if (f.from || f.to) count++;
        return count;
      },
      label: () => "filters",
      variant: "secondary",
      hideWhenZero: true,
    },
  ],
});

/* -------------------- Actions -------------------- */
function resetAll() {
  q.value = "";
  selectedEventTypes.value = [];
  entityType.value = "all";
  dateRange.value = [null, null];
  fetchPage(1);
}

function refresh() {
  fetchPage(currentPage.value || 1);
}

/* -------------------- Init -------------------- */
onMounted(() => {
  fetchPage(1);
});
</script>

<template>
  <div class="p-4 space-y-6">
    <OverviewHeader
      title="System Events"
      description="Audit log of important actions across the system."
      :loading="loading"
      :showRefresh="true"
      :stats="headerState"
      :show-search="true"
      v-model:searchModelValue="q"
      search-placeholder="Search by event, actor, entity id..."
      :show-reset="true"
      :reset-disabled="false"
      @refresh="refresh"
      @reset="resetAll"
    >
      <template #filters>
        <el-row :gutter="12" align="middle" class="w-full">
          <!-- Entity type -->
          <el-col :xs="24" :sm="8" :md="6">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 whitespace-nowrap"
                >Entity:</span
              >
              <el-select
                v-model="entityType"
                size="small"
                class="w-full"
                placeholder="All"
                :disabled="loading"
              >
                <el-option
                  v-for="opt in entityTypeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </div>
          </el-col>

          <!-- Event types -->
          <el-col :xs="24" :sm="10" :md="10">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 whitespace-nowrap"
                >Events:</span
              >
              <el-select
                v-model="selectedEventTypes"
                multiple
                filterable
                clearable
                size="small"
                class="w-full"
                placeholder="Select event types"
                :disabled="loading"
              >
                <el-option
                  v-for="opt in eventTypeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </div>
          </el-col>

          <!-- Date range -->
          <el-col :xs="24" :sm="6" :md="8">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 whitespace-nowrap">Date:</span>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                size="small"
                class="w-full"
                start-placeholder="From"
                end-placeholder="To"
                :disabled="loading"
              />
            </div>
          </el-col>
        </el-row>
      </template>

      <template #actions>
        <BaseButton
          plain
          :loading="loading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="refresh"
        >
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <!-- TABLE -->
    <el-card>
      <el-table :data="events" v-loading="loading" style="width: 100%">
        <el-table-column label="Time" min-width="180">
          <template #default="{ row }">
            <span class="text-xs">{{ new Date(row.at).toLocaleString() }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="event" label="Event" min-width="180" />

        <el-table-column label="Entity" min-width="220">
          <template #default="{ row }">
            <div class="text-xs">
              <div class="font-medium">{{ row.entity_type || "unknown" }}</div>
              <div class="text-gray-500 break-all">
                {{ row.entity_id || "-" }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Actor" min-width="220">
          <template #default="{ row }">
            <div class="text-xs">
              <div class="font-medium">{{ row.actor_display_name || "-" }}</div>
              <div class="text-gray-500 break-all">
                {{ row.actor_id || "-" }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="Source" min-width="160">
          <template #default="{ row }">
            <span class="text-xs">{{ row.source || "-" }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openEvent(row)">
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- PAGINATION -->
      <div class="mt-4 flex justify-end" v-if="totalRows > 0">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalRows"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="goPage"
          @size-change="(size: number) => setPageSize(size)"
        />
      </div>
    </el-card>

    <!-- DRAWER: Event Details -->
    <el-drawer
      v-model="drawerOpen"
      size="45%"
      direction="rtl"
      @close="closeDrawer"
    >
      <template #header>
        <div class="flex flex-col">
          <div class="text-sm font-semibold">
            {{ activeEvent?.event || "Event" }}
          </div>
          <div class="text-xs text-gray-500">
            {{
              activeEvent?.at ? new Date(activeEvent.at).toLocaleString() : ""
            }}
          </div>
        </div>
      </template>

      <div v-if="activeEvent" class="space-y-4">
        <el-descriptions border :column="1" size="small">
          <el-descriptions-item label="Event">
            {{ activeEvent.event }}
          </el-descriptions-item>
          <el-descriptions-item label="Entity Type">
            {{ activeEvent.entity_type }}
          </el-descriptions-item>
          <el-descriptions-item label="Entity ID">
            <span class="break-all">{{ activeEvent.entity_id || "-" }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Actor">
            {{ activeEvent.actor_display_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="Actor ID">
            <span class="break-all">{{ activeEvent.actor_id || "-" }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Source">
            {{ activeEvent.source || "-" }}
          </el-descriptions-item>
        </el-descriptions>

        <div>
          <div class="text-xs font-semibold mb-2">Meta</div>
          <el-input
            type="textarea"
            :autosize="{ minRows: 10, maxRows: 22 }"
            :model-value="prettyJson(activeEvent.meta ?? {})"
            readonly
          />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
:deep(.el-card__body) {
  padding: 16px;
}
</style>
