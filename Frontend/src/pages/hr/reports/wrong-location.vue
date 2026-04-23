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
  WrongLocationReportParams,
} from "~/api/hr_admin/attendance";
import type { ColumnConfig } from "~/components/types/tableEdit";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

definePageMeta({ layout: "default" });

const attendanceService = hrmsAdminService().attendance;
const loading = ref(false);
const rows = ref<AttendanceDTO[]>([]);

const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive<{
  review_status: string;
  start_date: string;
  end_date: string;
}>({ review_status: "", start_date: "", end_date: "" });

const columns: ColumnConfig<AttendanceDTO>[] = [
  { field: "id", label: "Attendance ID", minWidth: "180px", visible: true },
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
    field: "wrong_location_reason",
    label: "Reason",
    minWidth: "240px",
    visible: true,
    render: (row: AttendanceDTO) => row.wrong_location_reason || "-",
  },
  {
    field: "location_review_status",
    label: "Review Status",
    width: "150px",
    visible: true,
    slotName: "review_status",
  },
  {
    field: "admin_comment",
    label: "Admin Comment",
    minWidth: "220px",
    visible: true,
    render: (row: AttendanceDTO) => row.admin_comment || "-",
  },
];

const reviewSummary = computed(() => {
  const counts = { pending: 0, approved: 0, rejected: 0 };
  for (const row of rows.value) {
    const status = String(row.location_review_status || "").toLowerCase();
    if (status === "pending") counts.pending += 1;
    if (status === "approved") counts.approved += 1;
    if (status === "rejected") counts.rejected += 1;
  }
  return counts;
});

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

function reviewStatusType(
  status?: string | null,
): "warning" | "success" | "danger" | "info" {
  const map: Record<string, "warning" | "success" | "danger" | "info"> = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
  };
  return map[String(status || "").toLowerCase()] || "info";
}

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): WrongLocationReportParams {
  return {
    page,
    limit,
    review_status: filters.review_status.trim() || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
}

async function fetchReport(page = pagination.page, limit = pagination.limit) {
  loading.value = true;
  try {
    const response = await attendanceService.getWrongLocationReports(
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
  filters.review_status = "";
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
    :title="'Wrong Location Report'"
    :description="'Wrong-location review report using attendance wrong-location endpoint'"
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
      >Pending: {{ reviewSummary.pending }}</el-tag
    >
    <el-tag type="success" effect="plain"
      >Approved: {{ reviewSummary.approved }}</el-tag
    >
    <el-tag type="danger" effect="plain"
      >Rejected: {{ reviewSummary.rejected }}</el-tag
    >
  </div>

  <el-row :gutter="12" class="mb-4">
    <el-col :xs="24" :sm="8"
      ><ElInput
        v-model="filters.review_status"
        clearable
        placeholder="review_status"
        @keyup.enter="applyFilters"
    /></el-col>
    <el-col :xs="24" :sm="8"
      ><ElDatePicker
        v-model="filters.start_date"
        class="w-full"
        value-format="YYYY-MM-DD"
        placeholder="start_date"
    /></el-col>
    <el-col :xs="24" :sm="8"
      ><ElDatePicker
        v-model="filters.end_date"
        class="w-full"
        value-format="YYYY-MM-DD"
        placeholder="end_date"
    /></el-col>
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
    <template #review_status="{ row }">
      <ElTag
        :type="reviewStatusType(row.location_review_status)"
        effect="plain"
        round
        size="small"
      >
        {{ String(row.location_review_status || "-").toUpperCase() }}
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
