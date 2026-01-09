<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import { ElMessage } from "element-plus";
import dayjs from "dayjs";

import { storeToRefs } from "pinia";
import { studentService } from "~/api/student";
import type { AttendanceStatus } from "~/api/types/school.dto";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";

import { useHeaderState } from "~/composables/ui/useHeaderState";
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { reportError } from "~/utils/errors/errors";
import type { ColumnConfig } from "~/components/types/tableEdit";

import { usePreferencesStore } from "~/stores/preferencesStore";

const student = studentService();
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

/* ---------------------------------------------
 * Types (match backend response item)
 * ------------------------------------------- */
type AttendanceEnriched = {
  id: string;

  student_id: string;
  student_name?: string | null;

  class_id?: string | null;
  class_name?: string | null;

  subject_id?: string | null;
  subject_label?: string | null;

  schedule_slot_id?: string | null;
  day_of_week?: number | null; // tolerate 0..6 or 1..7
  start_time?: string | null; // "HH:MM"
  end_time?: string | null; // "HH:MM"
  room?: string | null;

  status: AttendanceStatus | string;
  record_date: string; // "YYYY-MM-DD"

  marked_by_teacher_id?: string | null;
  teacher_name?: string | null;

  lifecycle?: {
    created_at: string;
    updated_at: string;
    deleted_at?: string | null;
    deleted_by?: string | null;
  };
};

/* ---------------------------------------------
 * State
 * ------------------------------------------- */
const errorMessage = ref<string | null>(null);
let requestSeq = 0;

/* ---------------------------------------------
 * Client-side filters (apply to current page)
 * ------------------------------------------- */
const q = ref("");
const statusFilter = ref<"all" | "present" | "absent" | "excused">("all");
const dowFilter = ref<number | "all">("all");

/* ---------------------------------------------
 * Store-driven page size
 * ------------------------------------------- */
const effectivePageSize = computed(() => prefs.getTablePageSize());
const pageSizes = computed(() => prefs.getAllowedPageSizes());

/* ---------------------------------------------
 * Paginated fetch (store-driven pageSizeRef)
 * ------------------------------------------- */
const {
  data: rows,
  error,
  hasFetchedOnce,
  currentPage,
  pageSize,
  totalRows,
  initialLoading,
  fetching,
  fetchPage,
  goPage,
} = usePaginatedFetch<AttendanceEnriched, "all">(
  async (_filter, page, pageSize, signal) => {
    const res: any = await student.student.getMyAttendance(
      { page, page_size: pageSize } as any,
      { signal, showError: false }
    );

    // Support both shapes:
    // (A) wrap_response => res.data.items
    // (B) direct => res.items
    const items = (res?.data?.items ??
      res?.items ??
      []) as AttendanceEnriched[];
    const total = Number(res?.data?.total ?? res?.total ?? items.length) || 0;

    return { items, total };
  },
  {
    initialPage: 1,
    pageSizeRef: effectivePageSize,
    filter: computed(() => "all" as const),
  }
);

const loading = computed(() => initialLoading.value || fetching.value);

watch(
  () => error.value,
  (e) => {
    errorMessage.value = e ? e.message ?? "Failed to load attendance." : null;
  },
  { immediate: true }
);

/* ---------------------------------------------
 * Helpers
 * ------------------------------------------- */
const safeText = (v: any, fallback = "—") => {
  const s = String(v ?? "").trim();
  return s ? s : fallback;
};

const formatDate = (v: any) => {
  const d = dayjs(v);
  return d.isValid() ? d.format("YYYY-MM-DD") : safeText(v);
};

const normalizeDow = (v: any): number | null => {
  const n = Number(v);
  if (!Number.isFinite(n)) return null;
  if (n >= 0 && n <= 6) return n + 1; // 0-based -> ISO
  if (n >= 1 && n <= 7) return n; // ISO already
  return null;
};

const dowLabel = (isoDow: number | null) => {
  if (!isoDow) return "—";
  const names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  return names[isoDow - 1] ?? "—";
};

const formatTimeRange = (start?: string | null, end?: string | null) => {
  const s = safeText(start, "");
  const e = safeText(end, "");
  if (!s && !e) return "—";
  if (s && e) return `${s}–${e}`;
  return s || e;
};

const statusTag = (s?: AttendanceStatus | string | null) => {
  if (s === "present") return "success";
  if (s === "absent") return "danger";
  if (s === "excused") return "warning";
  return "info";
};

const statusAccent = (s?: AttendanceStatus | string | null) => {
  if (s === "present") return "var(--button-success-bg)";
  if (s === "absent") return "var(--button-danger-bg)";
  if (s === "excused") return "var(--button-warning-bg)";
  return "var(--color-primary)";
};

const formatStatusLabel = (s?: AttendanceStatus | string | null) => {
  if (!s) return "—";
  if (s === "present") return "Present";
  if (s === "absent") return "Absent";
  if (s === "excused") return "Excused";
  return String(s);
};

/* ---------------------------------------------
 * Filtered rows (client-side)
 * IMPORTANT: filters apply only to currently loaded page.
 * ------------------------------------------- */
const filteredRows = computed(() => {
  const text = q.value.trim().toLowerCase();
  const sf = statusFilter.value;
  const df = dowFilter.value;

  return rows.value.filter((r) => {
    const status = String(r.status ?? "").toLowerCase();

    if (sf !== "all" && status !== sf) return false;

    const iso = normalizeDow(r.day_of_week);
    if (df !== "all" && iso !== df) return false;

    if (!text) return true;

    const hay = [
      r.subject_label,
      r.teacher_name,
      r.class_name,
      r.room,
      r.status,
      r.record_date,
      r.start_time,
      r.end_time,
    ]
      .map((x) => String(x ?? "").toLowerCase())
      .join(" | ");

    return hay.includes(text);
  });
});

/* ---------------------------------------------
 * Columns
 * ------------------------------------------- */
type Row = AttendanceEnriched;

const studentAttendanceColumns: ColumnConfig<Row>[] = [
  {
    label: "Date",
    field: "record_date",
    minWidth: 140,
    showOverflowTooltip: true,
    render: (row) => formatDate((row as any).record_date),
  },
  {
    label: "Day",
    field: "day_of_week",
    minWidth: 110,
    showOverflowTooltip: true,
    render: (row) => dowLabel(normalizeDow((row as any).day_of_week)),
  },
  {
    label: "Time",
    field: "start_time",
    minWidth: 140,
    showOverflowTooltip: true,
    render: (row) =>
      formatTimeRange((row as any).start_time, (row as any).end_time),
  },
  {
    label: "Subject",
    field: "subject_label",
    minWidth: 260,
    showOverflowTooltip: true,
    render: (row) => safeText((row as any).subject_label),
  },
  {
    label: "Room",
    field: "room",
    minWidth: 140,
    showOverflowTooltip: true,
    render: (row) => safeText((row as any).room),
  },
  {
    label: "Status",
    field: "status",
    minWidth: 170,
    useSlot: true,
    slotName: "status",
  },
  {
    label: "Class",
    field: "class_name",
    minWidth: 220,
    showOverflowTooltip: true,
    render: (row) => safeText((row as any).class_name),
  },
  {
    label: "Teacher",
    field: "teacher_name",
    minWidth: 220,
    showOverflowTooltip: true,
    render: (row) => safeText((row as any).teacher_name),
  },
];

/* ---------------------------------------------
 * Stats (based on filteredRows)
 * ------------------------------------------- */
const statusSummary = computed(() => {
  const summary = {
    total: filteredRows.value.length,
    present: 0,
    absent: 0,
    excused: 0,
  };

  for (const rec of filteredRows.value) {
    const s = String(rec.status ?? "").toLowerCase();
    if (s === "present") summary.present++;
    else if (s === "absent") summary.absent++;
    else if (s === "excused") summary.excused++;
  }

  return summary;
});

const presentRate = computed(() => {
  if (!statusSummary.value.total) return null;
  return (
    Math.round(
      (statusSummary.value.present / statusSummary.value.total) * 1000
    ) / 10
  );
});

const { headerState } = useHeaderState({
  items: [
    {
      key: "total",
      getValue: () => statusSummary.value.total,
      singular: "record",
      plural: "records",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "present_rate",
      getValue: () => presentRate.value ?? 0,
      label: (value) =>
        presentRate.value === null ? undefined : `Present rate: ${value}%`,
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
    {
      key: "absent",
      getValue: () => statusSummary.value.absent,
      singular: "absent",
      plural: "absent",
      variant: "secondary",
      dotClass: "bg-red-500",
      hideWhenZero: true,
    },
  ],
});

/* ---------------------------------------------
 * Actions
 * ------------------------------------------- */
const loadAttendance = async (page = 1) => {
  const seq = ++requestSeq;
  errorMessage.value = null;

  try {
    await fetchPage(page);
    if (seq !== requestSeq) return;
  } catch (err) {
    if (seq !== requestSeq) return;
    reportError(err, "student.attendance.load", "log");
  }
};

const handleRefresh = async () => {
  if (loading.value) return;
  await loadAttendance(currentPage.value || 1);
  ElMessage.success("Attendance refreshed");
};

const clearError = () => {
  errorMessage.value = null;
};

const handlePageChange = (page: number) => {
  goPage(page);
};

const handlePageSizeChange = (size: number) => {
  // Source of truth is preferences store -> triggers usePaginatedFetch watcher
  prefs.setTablePageSize(size);
};

const resetFilters = () => {
  q.value = "";
  statusFilter.value = "all";
  dowFilter.value = "all";
};

/* ---------------------------------------------
 * Lifecycle
 * ------------------------------------------- */
onMounted(() => loadAttendance(1));
onBeforeUnmount(() => {
  requestSeq++;
});
</script>

<template>
  <div class="p-4 space-y-5 max-w-6xl mx-auto pb-10" v-loading="loading">
    <!-- IMPORTANT:
         Turn off OverviewHeader built-in reset/refresh/search
         so you don't get duplicate "Reset" buttons like your screenshot.
    -->
    <OverviewHeader
      title="My Attendance"
      description="View your attendance records by date, subject, and schedule."
      :loading="loading"
      :stats="headerState"
      :show-refresh="false"
      :show-search="false"
      :show-reset="false"
    >
      <template #actions>
        <div class="flex items-center gap-2">
          <BaseButton plain :loading="loading" @click="handleRefresh">
            Refresh
          </BaseButton>

          <BaseButton :disabled="loading" @click="resetFilters">
            Reset
          </BaseButton>
        </div>
      </template>

      <template #filters>
        <div class="space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <el-input
              v-model="q"
              clearable
              placeholder="Search subject, teacher, class, room..."
            />

            <el-select
              v-model="statusFilter"
              class="w-full"
              placeholder="Status"
            >
              <el-option label="All statuses" value="all" />
              <el-option label="Present" value="present" />
              <el-option label="Absent" value="absent" />
              <el-option label="Excused" value="excused" />
            </el-select>

            <el-select
              v-model="dowFilter"
              class="w-full"
              placeholder="Day of week"
            >
              <el-option label="All days" :value="'all'" />
              <el-option label="Mon" :value="1" />
              <el-option label="Tue" :value="2" />
              <el-option label="Wed" :value="3" />
              <el-option label="Thu" :value="4" />
              <el-option label="Fri" :value="5" />
              <el-option label="Sat" :value="6" />
              <el-option label="Sun" :value="7" />
            </el-select>
          </div>

          <div class="text-xs" style="color: var(--muted-color)">
            View-only. Attendance is recorded by your teacher. Filters apply to
            the currently loaded page.
          </div>
        </div>
      </template>
    </OverviewHeader>

    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="rounded-xl border border-red-200/60 shadow-sm"
        @close="clearError"
      />
    </transition>

    <!-- Skeleton first load -->
    <el-card
      v-if="loading && !hasFetchedOnce"
      shadow="never"
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    >
      <el-skeleton animated :rows="8" />
    </el-card>

    <!-- Empty -->
    <el-empty
      v-else-if="!loading && hasFetchedOnce && !filteredRows.length"
      description="No attendance records match your filters."
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    />

    <!-- Table -->
    <TableCard
      v-else
      title="Attendance records"
      description="Each row is one attendance record."
      :padding="'20px'"
      :rightText="`Showing ${filteredRows.length} / ${totalRows} records (page ${currentPage})`"
    >
      <SmartTable
        class="app-table"
        :data="filteredRows"
        :columns="studentAttendanceColumns"
        :loading="loading"
        :smartProps="{
          border: true,
          size: 'small',
          'highlight-current-row': true,
        }"
        :has-fetched-once="hasFetchedOnce"
      >
        <template #status="{ row }">
          <div class="flex items-center gap-2 min-w-0">
            <span
              class="inline-block h-2 w-2 rounded-full"
              :style="{ background: statusAccent(row.status) }"
            />
            <el-tag size="small" :type="statusTag(row.status)" effect="plain">
              {{ formatStatusLabel(row.status) }}
            </el-tag>
          </div>
        </template>
      </SmartTable>

      <div v-if="totalRows > 0" class="mt-4 flex justify-end">
        <el-pagination
          background
          layout="prev, pager, next, jumper, sizes, total"
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="pageSizes"
          :total="totalRows"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </TableCard>
  </div>
</template>

<style scoped>
:deep(.el-card) {
  border-radius: 16px;
}

:deep(.app-table) {
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-color);

  --el-table-header-bg-color: color-mix(
    in srgb,
    var(--color-card) 88%,
    var(--color-bg) 12%
  );
  --el-table-header-text-color: var(--text-color);

  --el-table-row-hover-bg-color: var(--hover-bg);
  --el-table-current-row-bg-color: var(--active-bg);
}

:deep(.app-table .el-table__header-wrapper th) {
  font-weight: 650;
  font-size: 13px;
}

:deep(.app-table.el-table--border .el-table__inner-wrapper::after),
:deep(.app-table.el-table--border::after),
:deep(.app-table.el-table--border::before) {
  background-color: var(--border-color);
}
</style>
