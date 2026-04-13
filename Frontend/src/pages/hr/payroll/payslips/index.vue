<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import {
  ElButton,
  ElCol,
  ElDatePicker,
  ElInput,
  ElMessage,
  ElPagination,
  ElRow,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type { PayslipDTO, PayslipListParams } from "~/api/hr_admin/payroll";
import type { ColumnConfig } from "~/components/types/tableEdit";

definePageMeta({ layout: "default" });

const payrollService = hrmsAdminService().payrollRun;

const loading = ref(false);
const rows = ref<PayslipDTO[]>([]);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  payroll_run_id: string;
  employee_id: string;
  month: string;
}>({
  payroll_run_id: "",
  employee_id: "",
  month: "",
});

const tableColumns: ColumnConfig<PayslipDTO>[] = [
  {
    field: "id",
    label: "Payslip ID",
    minWidth: "180px",
    visible: true,
  },
  {
    field: "payroll_run_id",
    label: "Payroll Run",
    minWidth: "180px",
    visible: true,
  },
  {
    field: "employee_id",
    label: "Employee",
    minWidth: "130px",
    visible: true,
  },
  {
    field: "month",
    label: "Month",
    width: "110px",
    visible: true,
  },
  {
    field: "base_salary",
    label: "Base Salary",
    width: "130px",
    visible: true,
    render: (row: PayslipDTO) => formatMoney(row.base_salary),
  },
  {
    field: "ot_payment",
    label: "OT Payment",
    width: "120px",
    visible: true,
    render: (row: PayslipDTO) => formatMoney(row.ot_payment),
  },
  {
    field: "total_deductions",
    label: "Deductions",
    width: "120px",
    visible: true,
    render: (row: PayslipDTO) => formatMoney(row.total_deductions),
  },
  {
    field: "net_salary",
    label: "Net Salary",
    width: "130px",
    visible: true,
    render: (row: PayslipDTO) => formatMoney(row.net_salary),
  },
  {
    field: "status",
    label: "Status",
    width: "120px",
    visible: true,
    slotName: "status",
  },
  {
    field: "lifecycle",
    label: "Created At",
    minWidth: "180px",
    visible: true,
    render: (row: PayslipDTO) => formatDateTime(row.lifecycle?.created_at),
  },
];

const activeFilterBadge = computed(() => {
  return [
    Boolean(filters.payroll_run_id.trim()),
    Boolean(filters.employee_id.trim()),
    Boolean(filters.month),
  ].filter(Boolean).length;
});

const totalNetSalary = computed(() => {
  return rows.value.reduce((sum, row) => sum + Number(row.net_salary || 0), 0);
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

function statusTagType(status?: string | null): "warning" | "success" | "info" {
  const map: Record<string, "warning" | "success" | "info"> = {
    generated: "warning",
    paid: "success",
  };
  return map[String(status || "").toLowerCase()] || "info";
}

function statusClass(status?: string | null): string {
  const map: Record<string, string> = {
    generated: "status-pill status-pill--draft",
    paid: "status-pill status-pill--paid",
  };
  return map[String(status || "").toLowerCase()] || "status-pill";
}

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): PayslipListParams {
  return {
    payroll_run_id: filters.payroll_run_id.trim() || undefined,
    employee_id: filters.employee_id.trim() || undefined,
    month: filters.month || undefined,
    page,
    limit,
  };
}

async function fetchPayslips(page = pagination.page, limit = pagination.limit) {
  loading.value = true;
  try {
    const response = await payrollService.listPayslips(
      buildParams(page, limit),
    );
    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.page_size ?? limit;
  } catch {
    ElMessage.error("Failed to load payslips");
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchPayslips(1, pagination.limit);
}

function resetFilters() {
  filters.payroll_run_id = "";
  filters.employee_id = "";
  filters.month = "";
  void applyFilters();
}

async function handlePageChange(page: number) {
  pagination.page = page;
  await fetchPayslips(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchPayslips(1, size);
}

import { onMounted } from "vue";
onMounted(() => {
  fetchPayslips(1, pagination.limit);
});
</script>

<template>
  <OverviewHeader
    :title="'Payroll Payslips'"
    :description="'Review all generated payslips with payroll run, employee, and month filters'"
    :backPath="'/hr/payroll/runs'"
  >
    <template #actions>
      <BaseButton
        plain
        :loading="loading"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="fetchPayslips(pagination.page, pagination.limit)"
      >
        Refresh
      </BaseButton>
    </template>
  </OverviewHeader>

  <div class="summary-strip">
    <el-tag effect="plain" class="summary-strip__tag">
      Total: {{ pagination.total }}
    </el-tag>
    <el-tag type="success" effect="plain" class="summary-strip__tag">
      Page Net Salary: {{ formatMoney(totalNetSalary) }}
    </el-tag>
  </div>

  <el-row :gutter="12" class="mb-4">
    <el-col :xs="24" :sm="12" :md="8" :lg="6">
      <ElInput
        v-model="filters.payroll_run_id"
        clearable
        placeholder="Filter by payroll_run_id"
        @keyup.enter="applyFilters"
      />
    </el-col>

    <el-col :xs="24" :sm="12" :md="8" :lg="6">
      <ElInput
        v-model="filters.employee_id"
        clearable
        placeholder="Filter by employee_id"
        @keyup.enter="applyFilters"
      />
    </el-col>

    <el-col :xs="24" :sm="12" :md="8" :lg="6">
      <ElDatePicker
        v-model="filters.month"
        type="month"
        class="w-full"
        value-format="YYYY-MM"
        placeholder="Filter by month"
      />
    </el-col>

    <el-col :xs="24" :sm="12" :md="24" :lg="6">
      <div class="filter-actions">
        <BaseButton type="primary" :loading="loading" @click="applyFilters">
          Apply Filters
          <span v-if="activeFilterBadge" class="filter-badge">{{
            activeFilterBadge
          }}</span>
        </BaseButton>
        <BaseButton plain :disabled="loading" @click="resetFilters">
          Reset
        </BaseButton>
      </div>
    </el-col>
  </el-row>

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
      @current-change="handlePageChange"
      @size-change="handlePageSizeChange"
    />
  </el-row>
</template>

<style scoped>
.summary-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.summary-strip__tag {
  font-weight: 600;
}

.filter-actions {
  height: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-badge {
  margin-left: 6px;
  padding: 0 6px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
  font-size: 12px;
  line-height: 18px;
}

.status-pill {
  font-weight: 600;
  letter-spacing: 0.01em;
}

.status-pill--draft {
  border-color: #e6a23c;
  color: #b88230;
  background: #fff8eb;
}

.status-pill--paid {
  border-color: #67c23a;
  color: #3b8f1d;
  background: #f1faec;
}
</style>
