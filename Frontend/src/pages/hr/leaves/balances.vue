<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  ElCard,
  ElInput,
  ElOption,
  ElPagination,
  ElSelect,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import PageToolbar from "~/components/page-toolbar/PageToolbar.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";
import { hrmsAdminService } from "~/api/hr_admin";
import type { LeaveBalanceItemDTO } from "~/api/hr_admin/leave";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { useHrEmployeeStore } from "~/stores/hrEmployeeStore";

definePageMeta({ layout: "default" });

const leaveService = hrmsAdminService().leaveRequest;
const employeeStore = useHrEmployeeStore();

const loading = ref(false);
const rows = ref<LeaveBalanceItemDTO[]>([]);
const totalRows = ref(0);

const pagination = reactive({
  page: 1,
  limit: 20,
});

const filters = reactive({
  q: "",
  employee_id: "",
});

const employeeOptionsLoading = ref(false);
const employeeOptions = ref<Array<{ value: string; label: string }>>([]);

const columns: ColumnConfig<LeaveBalanceItemDTO>[] = [
  {
    field: "employee_name",
    label: "Employee",
    minWidth: "220px",
    visible: true,
    render: (row: LeaveBalanceItemDTO) =>
      displayRelation(row.employee_name, row.employee_id),
  },
  {
    field: "manager_name",
    label: "Manager",
    minWidth: "180px",
    visible: true,
    render: (row: LeaveBalanceItemDTO) =>
      displayRelation(row.manager_name, row.manager_user_id),
  },
  {
    field: "department",
    label: "Department",
    minWidth: "140px",
    visible: true,
    render: (row: LeaveBalanceItemDTO) => String(row.department || "-"),
  },
  {
    field: "position",
    label: "Position",
    minWidth: "140px",
    visible: true,
    render: (row: LeaveBalanceItemDTO) => String(row.position || "-"),
  },
  {
    field: "annual_entitlement",
    label: "Entitlement",
    width: "120px",
    visible: true,
  },
  {
    field: "used_days",
    label: "Used",
    width: "100px",
    visible: true,
  },
  {
    field: "remaining_days",
    label: "Remaining",
    width: "110px",
    visible: true,
  },
  {
    field: "pending_days",
    label: "Pending",
    width: "100px",
    visible: true,
  },
  {
    field: "approved_days",
    label: "Approved",
    width: "110px",
    visible: true,
  },
  {
    field: "last_approved_end_date",
    label: "Last Approved End",
    width: "170px",
    visible: true,
    render: (row: LeaveBalanceItemDTO) => formatDate(row.last_approved_end_date),
  },
  {
    field: "employee_status",
    label: "Status",
    width: "120px",
    visible: true,
    slotName: "employee_status",
  },
];

const summary = computed(() => {
  const totalEmployees = rows.value.length;
  let totalRemaining = 0;
  let totalPending = 0;
  let totalApproved = 0;

  for (const row of rows.value) {
    totalRemaining += Number(row.remaining_days || 0);
    totalPending += Number(row.pending_days || 0);
    totalApproved += Number(row.approved_days || 0);
  }

  return {
    totalEmployees,
    totalRemaining,
    totalPending,
    totalApproved,
  };
});

function formatDate(value?: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
}

async function fetchEmployeeOptions() {
  employeeOptionsLoading.value = true;
  try {
    const response = await employeeStore.getEmployeesWithAccounts(
      {
        page: 1,
        limit: 500,
        with_accounts: true,
      },
      { showError: false },
    );

    employeeOptions.value = (response.items ?? [])
      .map((item) => ({
        value: item.employee.id,
        label: displayRelation(
          item.employee.employee_name || item.employee.full_name,
          item.employee.id,
          item.employee.employee_code || "Employee",
        ),
      }))
      .filter((item) => !!item.value);
  } catch {
    employeeOptions.value = [];
  } finally {
    employeeOptionsLoading.value = false;
  }
}

async function fetchBalances(
  page = pagination.page,
  limit = pagination.limit,
) {
  loading.value = true;
  try {
    const response = await leaveService.getBalances({
      page,
      limit,
      q: filters.q.trim() || undefined,
      employee_id: filters.employee_id || undefined,
    });
    rows.value = response.items ?? [];
    totalRows.value = Number(response.total ?? rows.value.length);
    pagination.page = Number(response.page ?? page);
    pagination.limit = Number(response.page_size ?? limit);
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchBalances(1, pagination.limit);
}

function resetFilters() {
  filters.q = "";
  filters.employee_id = "";
  void applyFilters();
}

async function handlePageChange(page: number) {
  pagination.page = page;
  await fetchBalances(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchBalances(1, size);
}

onMounted(async () => {
  await Promise.all([fetchEmployeeOptions(), fetchBalances(1, pagination.limit)]);
});
</script>

<template>
  <div class="leave-balance-page">
    <OverviewHeader
      title="Leave Balances"
      description="Track team leave entitlement, usage, pending, and remaining balances."
      :backPath="'/hr/leaves'"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="fetchBalances(pagination.page, pagination.limit)">
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <PageToolbar class="page-tool-bar">
      <template #left>
        <ElInput
          v-model="filters.q"
          clearable
          class="toolbar-search"
          placeholder="Search employee, code, department, position"
          @keyup.enter="applyFilters"
          @clear="applyFilters"
        />
      </template>
      <template #right>
        <ElSelect
          v-model="filters.employee_id"
          filterable
          clearable
          class="toolbar-select"
          placeholder="Select employee"
          :loading="employeeOptionsLoading"
          @change="applyFilters"
        >
          <ElOption
            v-for="item in employeeOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </ElSelect>
        <BaseButton plain @click="applyFilters">Apply</BaseButton>
        <BaseButton plain :disabled="!filters.q && !filters.employee_id" @click="resetFilters">
          Reset
        </BaseButton>
      </template>
    </PageToolbar>

    <div class="summary-strip">
      <ElTag effect="plain" class="summary-strip__tag">
        Employees: {{ summary.totalEmployees }}
      </ElTag>
      <ElTag type="success" effect="plain" class="summary-strip__tag">
        Remaining: {{ summary.totalRemaining }}
      </ElTag>
      <ElTag type="warning" effect="plain" class="summary-strip__tag">
        Pending: {{ summary.totalPending }}
      </ElTag>
      <ElTag type="info" effect="plain" class="summary-strip__tag">
        Approved: {{ summary.totalApproved }}
      </ElTag>
    </div>

    <ElCard class="table-shell" shadow="never">
      <SmartTable
        :data="rows"
        :columns="columns"
        :loading="loading"
        :has-fetched-once="true"
      >
        <template #employee_status="{ row }">
          <ElTag
            :type="String(row.employee_status || '').toLowerCase() === 'active' ? 'success' : 'warning'"
            effect="plain"
            size="small"
          >
            {{ row.employee_status || "-" }}
          </ElTag>
        </template>
      </SmartTable>

      <div v-if="totalRows > 0" class="pagination-wrap">
        <ElPagination
          :current-page="pagination.page"
          :page-size="pagination.limit"
          :total="totalRows"
          :page-sizes="[10, 20, 50, 100]"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </ElCard>
  </div>
</template>

<style scoped>
.leave-balance-page {
  padding: 16px;
  max-width: 1460px;
  margin: 0 auto;
  color: var(--text-color, var(--el-text-color-primary));
}

.page-tool-bar {
  margin-block: 12px;
}

.toolbar-search {
  min-width: min(460px, 100%);
}

.toolbar-select {
  min-width: 260px;
}

.summary-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.summary-strip__tag {
  border-radius: 999px;
  padding-inline: 10px;
}

.table-shell {
  border: 1px solid var(--border-color, var(--el-border-color-light));
  background: var(--color-card, var(--el-bg-color));
  box-shadow: var(--shadow-sm, 0 6px 16px rgba(16, 24, 40, 0.05));
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

@media (max-width: 900px) {
  .toolbar-select {
    min-width: 100%;
  }

  .pagination-wrap {
    justify-content: flex-start;
  }
}
</style>
