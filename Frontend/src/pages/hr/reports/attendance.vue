<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import {
  ElCol,
  ElDatePicker,
  ElInput,
  ElPagination,
  ElRow,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  AttendanceDTO,
  AttendanceListParams,
} from "~/api/hr_admin/attendance";
import type { ColumnConfig } from "~/components/types/tableEdit";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

definePageMeta({ layout: "default" });

const attendanceService = hrmsAdminService().attendance;
const loading = ref(false);
const rows = ref<AttendanceDTO[]>([]);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  employee_id: string;
  status: string;
  start_date: string;
  end_date: string;
}>({
  employee_id: "",
  status: "",
  start_date: "",
  end_date: "",
});

const columns: ColumnConfig<AttendanceDTO>[] = [
  {
    field: "employee_id",
    label: "Employee",
    minWidth: "130px",
    visible: true,
    render: (row: AttendanceDTO) =>
      displayRelation(row.employee_name, row.employee_id),
  },
  { field: "attendance_date", label: "Date", width: "120px", visible: true },
  {
    field: "check_in_time",
    label: "Check In",
    minWidth: "170px",
    visible: true,
    render: (row: AttendanceDTO) => formatDateTime(row.check_in_time),
  },
  {
    field: "check_out_time",
    label: "Check Out",
    minWidth: "170px",
    visible: true,
    render: (row: AttendanceDTO) => formatDateTime(row.check_out_time),
  },
  {
    field: "late_minutes",
    label: "Late",
    width: "90px",
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
    width: "150px",
    visible: true,
    slotName: "status",
  },
];

const statusCount = computed(() => {
  const counts: Record<string, number> = {};
  for (const row of rows.value) {
    const key = String(row.status || "unknown").toLowerCase();
    counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
});

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): AttendanceListParams {
  return {
    page,
    limit,
    employee_id: filters.employee_id.trim() || undefined,
    status: filters.status.trim() || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
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
  };
  return map[String(status || "").toLowerCase()] || "info";
}

async function fetchReport(page = pagination.page, limit = pagination.limit) {
  loading.value = true;
  try {
    const response = await attendanceService.getAttendances(
      buildParams(page, limit),
    );
    rows.value = response.items ?? [];
    pagination.total = response.pagination?.total ?? rows.value.length;
    pagination.page = response.pagination?.page ?? page;
    pagination.limit = response.pagination?.page_size ?? limit;
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchReport(1, pagination.limit);
}

function resetFilters() {
  filters.employee_id = "";
  filters.status = "";
  filters.start_date = "";
  filters.end_date = "";
  void applyFilters();
}

import { onMounted } from "vue";
onMounted(() => {
  fetchReport(1, pagination.limit);
});
</script>

<template>
  <OverviewHeader
    :title="'Attendance Report'"
    :description="'Attendance report using /api/hrms/attendance'"
    :backPath="'/hr'"
  >
    <template #actions>
      <BaseButton
        plain
        :loading="loading"
        @click="fetchReport(pagination.page, pagination.limit)"
      >
        Refresh
      </BaseButton>
    </template>
  </OverviewHeader>

  <div class="summary-strip">
    <el-tag effect="plain">Total: {{ pagination.total }}</el-tag>
    <el-tag type="warning" effect="plain"
      >Late: {{ statusCount.late || 0 }}</el-tag
    >
    <el-tag type="danger" effect="plain"
      >Absent: {{ statusCount.absent || 0 }}</el-tag
    >
  </div>

  <el-row :gutter="12" class="mb-4">
    <el-col :xs="24" :sm="12" :md="6">
      <ElInput
        v-model="filters.employee_id"
        clearable
        placeholder="Employee"
        @keyup.enter="applyFilters"
      />
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <ElInput
        v-model="filters.status"
        clearable
        placeholder="Status"
        @keyup.enter="applyFilters"
      />
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <ElDatePicker
        v-model="filters.start_date"
        class="w-full"
        value-format="YYYY-MM-DD"
        placeholder="Start date"
      />
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <ElDatePicker
        v-model="filters.end_date"
        class="w-full"
        value-format="YYYY-MM-DD"
        placeholder="End date"
      />
    </el-col>
  </el-row>

  <div class="filter-actions">
    <BaseButton type="primary" :loading="loading" @click="applyFilters"
      >Apply</BaseButton
    >
    <BaseButton plain :disabled="loading" @click="resetFilters"
      >Reset</BaseButton
    >
  </div>

  <SmartTable
    :columns="columns"
    :data="rows"
    :loading="loading"
    :total="pagination.total"
    :page="pagination.page"
    :page-size="pagination.limit"
    @page="fetchReport"
    @page-size="(size: number) => fetchReport(1, size)"
  >
    <template #status="{ row }">
      <ElTag
        :type="statusTagType(row.status)"
        effect="plain"
        round
        size="small"
      >
        {{ String(row.status || "-").toUpperCase() }}
      </ElTag>
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
      @current-change="fetchReport"
      @size-change="(size: number) => fetchReport(1, size)"
    />
  </el-row>
</template>

<style scoped>
.summary-strip {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.filter-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}
</style>
