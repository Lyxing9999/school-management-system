<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  ElCard,
  ElCol,
  ElEmpty,
  ElPagination,
  ElRow,
  ElTable,
  ElTableColumn,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type { PayslipDTO } from "~/api/hr_admin/payroll/dto";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const router = useRouter();
const payrollService = hrmsAdminService().payrollRun;

const loading = ref(false);
const rows = ref<PayslipDTO[]>([]);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const summaryCards = computed(() => {
  const totalNet = rows.value.reduce(
    (sum, row) => sum + Number(row.net_salary || 0),
    0,
  );
  const totalOt = rows.value.reduce(
    (sum, row) => sum + Number(row.ot_payment || 0),
    0,
  );
  const totalDeduction = rows.value.reduce(
    (sum, row) => sum + Number(row.total_deductions || 0),
    0,
  );

  return [
    {
      label: "Loaded Payslips",
      value: rows.value.length,
      hint: "Current page",
    },
    {
      label: "Net Salary",
      value: formatMoney(totalNet),
      hint: "Current page total",
    },
    {
      label: "OT Payment",
      value: formatMoney(totalOt),
      hint: "Current page total",
    },
    {
      label: "Deductions",
      value: formatMoney(totalDeduction),
      hint: "Current page total",
    },
  ];
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

function statusTagType(
  status?: string | null,
): "success" | "warning" | "danger" | "info" {
  const key = String(status || "").toLowerCase();
  if (key === "paid") return "success";
  if (key === "generated" || key === "draft") return "warning";
  if (key === "rejected") return "danger";
  return "info";
}

async function fetchPayslips(page = pagination.page, limit = pagination.limit) {
  loading.value = true;
  try {
    const response = await payrollService.listPayslips({ page, limit });
    rows.value = response.items ?? [];
    pagination.page = response.page ?? page;
    pagination.limit = response.page_size ?? limit;
    pagination.total = response.total ?? rows.value.length;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loading.value = false;
  }
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

function openDetail(row: PayslipDTO) {
  router.push(ROUTES.EMPLOYEE.PAYSLIP_DETAIL(row.id));
}

function refreshPage() {
  void fetchPayslips();
}

onMounted(() => {
  void fetchPayslips();
});
</script>

<template>
  <div class="employee-payslips-page">
    <OverviewHeader
      title="My Payslips"
      description="Payroll records from GET /api/hrms/payroll/payslips"
      :backPath="ROUTES.EMPLOYEE.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="refreshPage"
          >Refresh</BaseButton
        >
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="summary-row">
      <el-col
        v-for="card in summaryCards"
        :key="card.label"
        :xs="24"
        :sm="12"
        :lg="6"
      >
        <el-card class="summary-card" shadow="hover">
          <p class="summary-card__label">{{ card.label }}</p>
          <p class="summary-card__value">{{ card.value }}</p>
          <p class="summary-card__hint">{{ card.hint }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="table-card" v-loading="loading">
      <template v-if="rows.length">
        <div class="table-wrap">
          <el-table :data="rows" border stripe>
            <el-table-column prop="month" label="Month" min-width="110" />
            <el-table-column label="Base Salary" min-width="130">
              <template #default="{ row }">{{
                formatMoney(row.base_salary)
              }}</template>
            </el-table-column>
            <el-table-column label="OT" min-width="110">
              <template #default="{ row }">{{
                formatMoney(row.ot_payment)
              }}</template>
            </el-table-column>
            <el-table-column label="Deductions" min-width="130">
              <template #default="{ row }">{{
                formatMoney(row.total_deductions)
              }}</template>
            </el-table-column>
            <el-table-column label="Net Salary" min-width="140">
              <template #default="{ row }">{{
                formatMoney(row.net_salary)
              }}</template>
            </el-table-column>
            <el-table-column label="Status" min-width="120">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" effect="plain" round>
                  {{ String(row.status || "-").toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Created" min-width="180">
              <template #default="{ row }">{{
                formatDateTime(row.lifecycle?.created_at)
              }}</template>
            </el-table-column>
            <el-table-column label="Action" width="110" fixed="right">
              <template #default="{ row }">
                <BaseButton plain size="small" @click="openDetail(row)"
                  >View</BaseButton
                >
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="pagination-wrap">
          <el-pagination
            :current-page="pagination.page"
            :page-size="pagination.limit"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @current-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>
      </template>

      <el-empty v-else description="No payslips found" />
    </el-card>
  </div>
</template>

<style scoped>
.employee-payslips-page {
  padding: 16px;
  max-width: 1440px;
  margin: 0 auto;
}

.summary-row {
  margin-bottom: 14px;
}

.summary-card {
  border-radius: 14px;
  min-height: 120px;
}

.summary-card__label {
  margin: 0;
  color: var(--muted-color, var(--el-text-color-secondary));
  font-size: 12px;
  text-transform: uppercase;
}

.summary-card__value {
  margin: 6px 0 4px;
  font-size: 26px;
  font-weight: 800;
  color: var(--text-color, var(--el-text-color-primary));
}

.summary-card__hint {
  margin: 0;
  color: var(--muted-color, var(--el-text-color-secondary));
  font-size: 12px;
}

.table-card {
  border-radius: 14px;
}

.table-wrap {
  overflow-x: auto;
}

.table-wrap :deep(.el-table) {
  min-width: 980px;
}

.pagination-wrap {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .employee-payslips-page {
    padding: 10px;
  }

  .summary-card__value {
    font-size: 22px;
  }

  .pagination-wrap {
    justify-content: center;
  }
}
</style>
