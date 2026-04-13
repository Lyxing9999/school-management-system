<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { RefreshLeft } from "@element-plus/icons-vue";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";

import type {
  HrEmployeeDTO,
  HrEmploymentType,
} from "~/api/hr_admin/employees/dto";
import { useHrEmployeeStore } from "~/stores/hrEmployeeStore";

definePageMeta({ layout: "default" });

interface ArchivedEmployeeRow {
  id: string;
  employee_code: string;
  full_name: string;
  department: string | null;
  position: string | null;
  employment_type: HrEmploymentType;
  status: "active" | "inactive";
  deleted_at: string | null;
}

const employeeStore = useHrEmployeeStore();

const loading = ref(false);
const rows = ref<ArchivedEmployeeRow[]>([]);
const totalRows = ref(0);
const page = ref(1);
const pageSize = ref(10);
const q = ref("");
const rowLoading = ref<Record<string, boolean>>({});

const columns: ColumnConfig<ArchivedEmployeeRow>[] = [
  { field: "full_name", label: "Employee", minWidth: "240px" },
  { field: "employee_code", label: "Code", width: "130px" },
  { field: "department", label: "Department", minWidth: "180px" },
  { field: "position", label: "Position", minWidth: "160px" },
  { field: "employment_type", label: "Employment", width: "130px" },
  { field: "lifecycle.deleted_at", label: "Deleted At", minWidth: "190px" },
  {
    field: "id",
    label: "Actions",
    operation: true,
    useSlot: true,
    slotName: "operation",
    fixed: "right",
    width: "140px",
  },
];

function toRow(employee: HrEmployeeDTO): ArchivedEmployeeRow {
  return {
    id: employee.id,
    employee_code: employee.employee_code,
    full_name: employee.full_name,
    department: employee.department ?? null,
    position: employee.position ?? null,
    employment_type: employee.employment_type,
    status: employee.status,
    deleted_at: employee.lifecycle?.deleted_at ?? null,
  };
}

function mapError(error: unknown, fallback: string) {
  if (error && typeof error === "object" && "response" in error) {
    const e = error as {
      response?: { data?: { user_message?: string; message?: string } };
    };
    return (
      e.response?.data?.user_message || e.response?.data?.message || fallback
    );
  }
  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

async function loadArchived() {
  loading.value = true;
  try {
    const response = await employeeStore.getEmployeesWithAccounts({
      page: page.value,
      limit: pageSize.value,
      q: q.value.trim() || undefined,
      deleted_only: true,
      with_accounts: true,
    });

    rows.value = (response.items ?? []).map((item) => toRow(item.employee));
    totalRows.value = Number(response.total ?? 0);
  } catch (error) {
    ElMessage.error(mapError(error, "Failed to load archived employees"));
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  page.value = 1;
  loadArchived();
}

function handlePageChange(value: number) {
  page.value = value;
  loadArchived();
}

async function restoreEmployee(row: ArchivedEmployeeRow) {
  try {
    await ElMessageBox.confirm(
      `Restore ${row.full_name}?`,
      "Restore Employee",
      {
        type: "info",
        confirmButtonText: "Restore",
        cancelButtonText: "Cancel",
      },
    );

    rowLoading.value[row.id] = true;
    await employeeStore.restoreEmployee(row.id);
    ElMessage.success("Employee restored successfully");
    await loadArchived();
  } catch (error: any) {
    if (error === "cancel" || error === "close") return;
    ElMessage.error(mapError(error, "Failed to restore employee"));
  } finally {
    rowLoading.value[row.id] = false;
  }
}

onMounted(() => {
  loadArchived();
});
</script>

<template>
  <div class="archived-page">
    <OverviewHeader
      title="Archived Employees"
      description="View deleted employees and restore records"
      @refresh="loadArchived"
    >
      <template #actions>
        <div class="header-actions">
          <el-input
            v-model="q"
            clearable
            placeholder="Search by name, code, department"
            class="search-input"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
          <BaseButton type="primary" @click="handleSearch">Search</BaseButton>
        </div>
      </template>
    </OverviewHeader>

    <el-card shadow="never" class="table-card">
      <SmartTable
        :columns="columns"
        :data="rows"
        :loading="loading"
        :total="totalRows"
        :page="page"
        :page-size="pageSize"
        @page="handlePageChange"
      >
        <template #operation="{ row }">
          <BaseButton
            type="success"
            link
            size="small"
            :loading="rowLoading[(row as ArchivedEmployeeRow).id]"
            @click="restoreEmployee(row as ArchivedEmployeeRow)"
          >
            <template #iconPre>
              <el-icon><RefreshLeft /></el-icon>
            </template>
            Restore
          </BaseButton>
        </template>
      </SmartTable>
    </el-card>
  </div>
</template>

<style scoped>
.archived-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.search-input {
  min-width: 280px;
}

.table-card {
  border: 1px solid color-mix(in srgb, var(--el-border-color) 75%, #ffffff 25%);
}
</style>
