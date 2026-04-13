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
  OvertimeRequestDTO,
  OvertimeRequestListParams,
} from "~/api/hr_admin/overtime";
import type { OvertimePayrollSummaryDTO } from "~/api/hr_admin/overtime";
import type { ColumnConfig } from "~/components/types/tableEdit";

definePageMeta({ layout: "default" });

const overtimeService = hrmsAdminService().overtimeRequest;
const loading = ref(false);
const summaryLoading = ref(false);
const rows = ref<OvertimeRequestDTO[]>([]);
const summary = ref<OvertimePayrollSummaryDTO | null>(null);

const pagination = reactive({ page: 1, limit: 10, total: 0 });
const filters = reactive<{
  employee_id: string;
  status: string;
  start_date: string;
  end_date: string;
}>({ employee_id: "", status: "", start_date: "", end_date: "" });

const columns: ColumnConfig<OvertimeRequestDTO>[] = [
  { field: "id", label: "Request ID", minWidth: "170px", visible: true },
  { field: "employee_id", label: "Employee", minWidth: "130px", visible: true },
  {
    field: "request_date",
    label: "Request Date",
    width: "130px",
    visible: true,
  },
  {
    field: "approved_hours",
    label: "Hours",
    width: "100px",
    visible: true,
    render: (row: OvertimeRequestDTO) =>
      Number(row.approved_hours || 0).toFixed(1),
  },
  {
    field: "calculated_payment",
    label: "Payment",
    width: "120px",
    visible: true,
    render: (row: OvertimeRequestDTO) => formatMoney(row.calculated_payment),
  },
  {
    field: "status",
    label: "Status",
    width: "120px",
    visible: true,
    slotName: "status",
  },
  {
    field: "submitted_at",
    label: "Submitted",
    minWidth: "170px",
    visible: true,
    render: (row: OvertimeRequestDTO) => formatDateTime(row.submitted_at),
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

function formatMoney(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "-";
  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
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

function statusType(
  status?: string | null,
): "warning" | "success" | "danger" | "info" {
  const map: Record<string, "warning" | "success" | "danger" | "info"> = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
    cancelled: "info",
  };
  return map[String(status || "").toLowerCase()] || "info";
}

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): OvertimeRequestListParams {
  return {
    page,
    limit,
    employee_id: filters.employee_id.trim() || undefined,
    status: (filters.status.trim() || undefined) as any,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
}

function buildSummaryParams() {
  return {
    employee_id: filters.employee_id.trim() || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
}

async function fetchRequests(page = pagination.page, limit = pagination.limit) {
  loading.value = true;
  try {
    const response = await overtimeService.getRequests(
      buildParams(page, limit),
    );
    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.limit ?? limit;
  } finally {
    loading.value = false;
  }
}

async function fetchSummary() {
  summaryLoading.value = true;
  try {
    summary.value = await overtimeService.getPayrollOvertimeSummary(
      buildSummaryParams(),
    );
  } finally {
    summaryLoading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await Promise.all([fetchRequests(1, pagination.limit), fetchSummary()]);
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
  void Promise.all([fetchRequests(1, pagination.limit), fetchSummary()]);
});
</script>

<template>
  <OverviewHeader
    :title="'Overtime Report'"
    :description="'Overtime report using requests and payroll summary endpoints'"
    :backPath="'/hr'"
  >
    <template #actions>
      <BaseButton
        plain
        :loading="loading || summaryLoading"
        @click="applyFilters"
        >Refresh</BaseButton
      >
    </template>
  </OverviewHeader>

  <div class="summary-strip">
    <el-tag effect="plain">Requests: {{ pagination.total }}</el-tag>
    <el-tag type="success" effect="plain"
      >Approved: {{ statusCount.approved || 0 }}</el-tag
    >
    <el-tag type="info" effect="plain"
      >OT Hours:
      {{ Number(summary?.total_approved_hours || 0).toFixed(1) }}</el-tag
    >
    <el-tag type="success" effect="plain"
      >OT Payment: {{ formatMoney(summary?.total_approved_payment) }}</el-tag
    >
  </div>

  <el-row :gutter="12" class="mb-4">
    <el-col :xs="24" :sm="12" :md="6"
      ><ElInput
        v-model="filters.employee_id"
        clearable
        placeholder="employee_id"
        @keyup.enter="applyFilters"
    /></el-col>
    <el-col :xs="24" :sm="12" :md="6"
      ><ElInput
        v-model="filters.status"
        clearable
        placeholder="status"
        @keyup.enter="applyFilters"
    /></el-col>
    <el-col :xs="24" :sm="12" :md="6"
      ><ElDatePicker
        v-model="filters.start_date"
        class="w-full"
        value-format="YYYY-MM-DD"
        placeholder="start_date"
    /></el-col>
    <el-col :xs="24" :sm="12" :md="6"
      ><ElDatePicker
        v-model="filters.end_date"
        class="w-full"
        value-format="YYYY-MM-DD"
        placeholder="end_date"
    /></el-col>
  </el-row>

  <div class="filter-actions">
    <BaseButton
      type="primary"
      :loading="loading || summaryLoading"
      @click="applyFilters"
      >Apply</BaseButton
    >
    <BaseButton
      plain
      :disabled="loading || summaryLoading"
      @click="resetFilters"
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
    @page="fetchRequests"
    @page-size="(size: number) => fetchRequests(1, size)"
  >
    <template #status="{ row }">
      <ElTag :type="statusType(row.status)" effect="plain" round size="small">
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
      @current-change="fetchRequests"
      @size-change="(size: number) => fetchRequests(1, size)"
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
