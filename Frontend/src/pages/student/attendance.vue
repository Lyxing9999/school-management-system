<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";
import { ElMessage } from "element-plus";

import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
dayjs.extend(utc);
dayjs.extend(timezone);

import { studentService } from "~/api/student";
import type { AttendanceDTO, AttendanceStatus } from "~/api/types/school.dto";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { useHeaderState } from "~/composables/ui/useHeaderState";
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { reportError } from "~/utils/errors/errors";
import type { ColumnConfig } from "~/components/types/tableEdit";

const student = studentService();

/* ---------------- types ---------------- */
type AttendanceEnriched = AttendanceDTO & {
  class_name?: string;
  teacher_name?: string;
  student_name?: string;
};

/* ---------------- state ---------------- */
const errorMessage = ref<string | null>(null);

/** prevent stale responses overriding newer refreshes */
let requestSeq = 0;
const hasFetchedOnce = ref(false);

/* ---------------- pagination + data ---------------- */
const {
  data: rows,
  loading,
  error,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<AttendanceEnriched, string>(
  async (_key, page, pageSize, signal) => {
    // VIEW-ONLY: no filters yet, just fetch
    const res = await student.student.getMyAttendance(
      { page, page_size: pageSize } as any,
      { signal, showError: false }
    );

    const items = (res?.items ?? []) as AttendanceEnriched[];
    const total = res?.total ?? items.length;

    return { items, total };
  },
  1,
  10,
  "all"
);

watch(
  () => error.value,
  (e) => {
    errorMessage.value = e ? e.message ?? "Failed to load attendance." : null;
  },
  { immediate: true }
);

/* ---------------- helpers ---------------- */
const statusTag = (s?: AttendanceStatus | string | null) => {
  if (s === "present") return "success";
  if (s === "absent") return "danger";
  if (s === "excused") return "warning";
  return "info";
};

const formatStatusLabel = (s?: AttendanceStatus | string | null) => {
  if (!s) return "—";
  if (s === "present") return "Present";
  if (s === "absent") return "Absent";
  if (s === "excused") return "Excused";
  return String(s);
};

/* ---------------- columns (SmartTable ColumnConfig) ---------------- */
type Row = AttendanceEnriched;

const studentAttendanceColumns: ColumnConfig<Row>[] = [
  {
    label: "Date",
    field: "record_date",
    minWidth: 140,
    showOverflowTooltip: true,
    render: (row) => {
      const v = (row as any).record_date;
      if (!v) return "—";
      const d = dayjs(v);
      return d.isValid() ? d.format("YYYY-MM-DD") : String(v);
    },
  },
  {
    label: "Status",
    field: "status",
    minWidth: 140,
    useSlot: true,
    slotName: "status",
  },
  {
    label: "Class",
    field: "class_name",
    minWidth: 220,
    showOverflowTooltip: true,
  },
  {
    label: "Teacher",
    field: "teacher_name",
    minWidth: 200,
    showOverflowTooltip: true,
  },
];

/* ---------------- derived stats ---------------- */
const statusSummary = computed(() => {
  const summary = {
    total: rows.value.length,
    present: 0,
    absent: 0,
    excused: 0,
  };
  for (const rec of rows.value) {
    if (rec.status === "present") summary.present++;
    else if (rec.status === "absent") summary.absent++;
    else if (rec.status === "excused") summary.excused++;
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

/* ---------------- actions ---------------- */
const loadAttendance = async (page = 1) => {
  const seq = ++requestSeq;
  errorMessage.value = null;

  try {
    await fetchPage(page);
    if (seq !== requestSeq) return;
    hasFetchedOnce.value = true;
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

/* ---------------- pagination ---------------- */
const handlePageChange = (page: number) => goPage(page);

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  fetchPage(1);
};

/* ---------------- lifecycle ---------------- */
onMounted(() => loadAttendance(1));
onBeforeUnmount(() => {
  requestSeq++;
});
</script>

<template>
  <div class="p-4 space-y-5 max-w-6xl mx-auto pb-10" v-loading="loading">
    <OverviewHeader
      title="My Attendance"
      description="View your attendance records."
      :loading="loading"
      :stats="headerState"
      :show-refresh="true"
      :show-search="false"
      :show-reset="false"
      @refresh="handleRefresh"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="handleRefresh">
          Refresh
        </BaseButton>
      </template>

      <template #filters>
        <div class="text-xs" style="color: var(--muted-color)">
          View-only. Attendance is recorded by your teacher.
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
      v-else-if="!loading && hasFetchedOnce && !rows.length"
      description="No attendance records yet."
      class="rounded-2xl border"
      style="
        background: color-mix(in srgb, var(--color-card) 96%, transparent);
        border-color: var(--border-color);
      "
    />

    <TableCard
      v-else
      title="Attendance records"
      description="Each row is one attendance record."
      :padding="'20px'"
      :rightText="`Showing ${rows.length} / ${totalRows} records`"
    >
      <SmartTable
        :data="rows"
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
          <el-tag size="small" :type="statusTag(row.status)" effect="plain">
            {{ formatStatusLabel(row.status) }}
          </el-tag>
        </template>
      </SmartTable>

      <div v-if="totalRows > 0" class="mt-4 flex justify-end">
        <el-pagination
          background
          layout="prev, pager, next, jumper, sizes, total"
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50]"
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
</style>
