<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  ElButton,
  ElDatePicker,
  ElInput,
  ElMessage,
  ElOption,
  ElPagination,
  ElRow,
  ElSelect,
  ElSwitch,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import PageToolbar from "~/components/page-toolbar/PageToolbar.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  AttendanceDTO,
  AttendanceListParams,
} from "~/api/hr_admin/attendance";
import type { ColumnConfig } from "~/components/types/tableEdit";

definePageMeta({ layout: "default" });

const attendanceService = hrmsAdminService().attendance;

const loading = ref(false);
const rows = ref<AttendanceDTO[]>([]);
const hasFetchedOnce = ref(false);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  employee_id: string;
  status: string | undefined;
  start_date: string;
  end_date: string;
  include_deleted: boolean;
  deleted_only: boolean;
}>({
  employee_id: "",
  status: undefined,
  start_date: "",
  end_date: "",
  include_deleted: false,
  deleted_only: false,
});

const tableColumns: ColumnConfig<AttendanceDTO>[] = [
  {
    field: "employee_id",
    label: "Employee",
    minWidth: "120px",
    visible: true,
  },
  {
    field: "attendance_date",
    label: "Date",
    width: "130px",
    visible: true,
    render: (row: AttendanceDTO) => formatDate(row.attendance_date),
  },
  {
    field: "check_in_time",
    label: "Check In",
    width: "165px",
    visible: true,
    render: (row: AttendanceDTO) => formatDateTime(row.check_in_time),
  },
  {
    field: "check_out_time",
    label: "Check Out",
    width: "165px",
    visible: true,
    render: (row: AttendanceDTO) => formatDateTime(row.check_out_time),
  },
  {
    field: "late_minutes",
    label: "Late",
    width: "95px",
    visible: true,
    render: (row: AttendanceDTO) =>
      row.late_minutes > 0 ? `${row.late_minutes} min` : "-",
  },
  {
    field: "early_leave_minutes",
    label: "Early Leave",
    width: "110px",
    visible: true,
    render: (row: AttendanceDTO) =>
      row.early_leave_minutes > 0 ? `${row.early_leave_minutes} min` : "-",
  },
  {
    field: "status",
    label: "Status",
    width: "180px",
    visible: true,
    slotName: "status",
  },
  {
    field: "admin_comment",
    label: "Admin Comment",
    minWidth: "180px",
    visible: true,
    render: (row: AttendanceDTO) => row.admin_comment || "-",
  },
  {
    field: "wrong_location_reason",
    label: "Wrong-Location Reason",
    minWidth: "200px",
    visible: false,
    render: (row: AttendanceDTO) => row.wrong_location_reason || "-",
  },
  {
    field: "id",
    operation: true,
    label: "Actions",
    width: "100px",
    fixed: "right",
    visible: true,
    slotName: "operation",
  },
];

const activeFilterBadge = computed(() => {
  const count = [
    Boolean(filters.employee_id.trim()),
    Boolean(filters.status),
    Boolean(filters.start_date),
    Boolean(filters.end_date),
    filters.include_deleted,
    filters.deleted_only,
  ].filter(Boolean).length;

  return count;
});

function formatDate(value?: string | null): string {
  if (!value) return "-";

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-");
    return new Date(
      Number(year),
      Number(month) - 1,
      Number(day),
    ).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
}

function formatDateTime(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function statusLabel(status?: string | null): string {
  const map: Record<string, string> = {
    checked_in: "Checked In",
    checked_out: "Checked Out",
    late: "Late",
    early_leave: "Early Leave",
    absent: "Absent",
    wrong_location_pending: "Wrong Location Pending",
    wrong_location_approved: "Wrong Location Approved",
    wrong_location_rejected: "Wrong Location Rejected",
  };
  return map[String(status || "").toLowerCase()] || String(status || "Unknown");
}

function statusTagType(
  status?: string | null,
): "warning" | "success" | "danger" | "info" | "primary" {
  const map: Record<
    string,
    "warning" | "success" | "danger" | "info" | "primary"
  > = {
    checked_in: "primary",
    checked_out: "success",
    late: "warning",
    early_leave: "warning",
    absent: "danger",
    wrong_location_pending: "warning",
    wrong_location_approved: "success",
    wrong_location_rejected: "danger",
  };

  return map[String(status || "").toLowerCase()] || "info";
}

function statusClass(status?: string | null): string {
  const map: Record<string, string> = {
    checked_in: "status-pill status-pill--info",
    checked_out: "status-pill status-pill--approved",
    late: "status-pill status-pill--pending",
    early_leave: "status-pill status-pill--pending",
    absent: "status-pill status-pill--rejected",
    wrong_location_pending: "status-pill status-pill--pending",
    wrong_location_approved: "status-pill status-pill--approved",
    wrong_location_rejected: "status-pill status-pill--rejected",
  };
  return map[String(status || "").toLowerCase()] || "status-pill";
}

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): AttendanceListParams {
  return {
    page,
    limit,
    employee_id: filters.employee_id.trim() || undefined,
    status: filters.status || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
    include_deleted: filters.deleted_only ? true : filters.include_deleted,
    deleted_only: filters.deleted_only || undefined,
  };
}

async function fetchAttendances(
  page = pagination.page,
  limit = pagination.limit,
) {
  loading.value = true;
  try {
    const response = await attendanceService.getAttendances(
      buildParams(page, limit),
    );
    rows.value = response.items ?? [];
    pagination.total = response.pagination?.total ?? rows.value.length;
    pagination.page = response.pagination?.page ?? page;
    pagination.limit = response.pagination?.page_size ?? limit;
  } catch {
    ElMessage.error("Failed to load attendance records");
  } finally {
    loading.value = false;
    hasFetchedOnce.value = true;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchAttendances(1, pagination.limit);
}

function resetFilters() {
  filters.employee_id = "";
  filters.status = undefined;
  filters.start_date = "";
  filters.end_date = "";
  filters.include_deleted = false;
  filters.deleted_only = false;
  applyFilters();
}

async function handlePageChange(page: number) {
  pagination.page = page;
  await fetchAttendances(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchAttendances(1, size);
}

function showDetails(row: AttendanceDTO) {
  ElMessage.info(
    `Attendance ${row.id} | ${statusLabel(row.status)} | ${formatDate(
      row.attendance_date,
    )}`,
  );
}

watch(
  () => filters.deleted_only,
  (deletedOnly) => {
    if (deletedOnly) {
      filters.include_deleted = true;
    }
  },
);

onMounted(() => {
  fetchAttendances(1, pagination.limit);
});
</script>

<template>
  <OverviewHeader
    :title="'Attendance Overview'"
    :description="'Review all attendance records with lifecycle and status filters'"
    :backPath="'/hr/dashboard'"
  >
    <template #actions>
      <BaseButton
        plain
        :loading="loading"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="fetchAttendances(pagination.page, pagination.limit)"
      >
        Refresh
      </BaseButton>
    </template>
  </OverviewHeader>

  <PageToolbar class="page-toolbar">
    <template #left>
      <ElInput
        v-model="filters.employee_id"
        clearable
        placeholder="Filter by employee_id"
        class="toolbar-input"
      />

      <ElSelect
        v-model="filters.status"
        clearable
        placeholder="Status"
        class="toolbar-select"
      >
        <ElOption label="Checked In" value="checked_in" />
        <ElOption label="Checked Out" value="checked_out" />
        <ElOption label="Late" value="late" />
        <ElOption label="Early Leave" value="early_leave" />
        <ElOption label="Absent" value="absent" />
        <ElOption
          label="Wrong Location Pending"
          value="wrong_location_pending"
        />
        <ElOption
          label="Wrong Location Approved"
          value="wrong_location_approved"
        />
        <ElOption
          label="Wrong Location Rejected"
          value="wrong_location_rejected"
        />
      </ElSelect>

      <ElDatePicker
        v-model="filters.start_date"
        type="date"
        value-format="YYYY-MM-DD"
        format="YYYY-MM-DD"
        placeholder="Start date"
        class="toolbar-date"
      />

      <ElDatePicker
        v-model="filters.end_date"
        type="date"
        value-format="YYYY-MM-DD"
        format="YYYY-MM-DD"
        placeholder="End date"
        class="toolbar-date"
      />
    </template>

    <template #right>
      <div class="filter-switches">
        <div class="filter-switch">
          <span class="filter-switch__label">Include deleted</span>
          <ElSwitch
            v-model="filters.include_deleted"
            :disabled="filters.deleted_only"
            size="small"
          />
        </div>

        <div class="filter-switch">
          <span class="filter-switch__label">Deleted only</span>
          <ElSwitch v-model="filters.deleted_only" size="small" />
        </div>
      </div>

      <BaseButton type="primary" :loading="loading" @click="applyFilters">
        Apply Filters
        <span v-if="activeFilterBadge" class="filter-badge">{{
          activeFilterBadge
        }}</span>
      </BaseButton>

      <BaseButton plain :disabled="loading" @click="resetFilters">
        Reset
      </BaseButton>
    </template>
  </PageToolbar>

  <SmartTable
    :columns="tableColumns"
    :data="rows"
    :loading="loading"
    :total="pagination.total"
    :page="pagination.page"
    :page-size="pagination.limit"
    @page="handlePageChange"
    @page-size="handlePageSizeChange"
  >
    <template #status="{ row }">
      <ElTag
        :type="statusTagType(row.status)"
        effect="plain"
        round
        size="small"
        :class="statusClass(row.status)"
      >
        {{ statusLabel(row.status) }}
      </ElTag>
    </template>

    <template #operation="{ row }">
      <ElButton
        type="info"
        link
        size="small"
        @click="showDetails(row as AttendanceDTO)"
      >
        View
      </ElButton>
    </template>
  </SmartTable>

  <el-row v-if="pagination.total > 0" justify="end" class="m-4">
    <ElPagination
      :current-page="pagination.page"
      :page-size="pagination.limit"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      background
      @current-change="handlePageChange"
      @size-change="handlePageSizeChange"
    />
  </el-row>
</template>

<style scoped>
.page-toolbar {
  margin-bottom: 16px;
}

.toolbar-input {
  min-width: 200px;
  max-width: 100%;
}

.toolbar-select {
  min-width: 160px;
}

.toolbar-date {
  min-width: 140px;
}

.filter-switches {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-switch {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-switch__label {
  font-size: 13px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
}

.filter-badge {
  margin-left: 6px;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 11px;
  line-height: 18px;
  background: color-mix(in srgb, var(--color-primary) 20%, white 80%);
  color: var(--color-primary);
}

.status-pill {
  font-weight: 600;
  letter-spacing: 0.01em;
}

.status-pill--pending {
  border-color: #e6a23c;
  color: #b88230;
  background: #fff8eb;
}

.status-pill--approved {
  border-color: #67c23a;
  color: #3b8f1d;
  background: #f1faec;
}

.status-pill--rejected {
  border-color: #f56c6c;
  color: #c74141;
  background: #fff2f2;
}

.status-pill--info {
  border-color: #909399;
  color: #61656d;
  background: #f5f6f7;
}
</style>
