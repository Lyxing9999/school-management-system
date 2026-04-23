<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  ElCard,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElOption,
  ElPagination,
  ElSelect,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeRowActions from "~/components/hrms/employees/EmployeeRowActions.vue";
import EmployeeOnboardDialog from "~/components/hrms/employees/EmployeeOnboardDialog.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import { ROUTES } from "~/constants/routes";
import { useHrEmployeeStore } from "~/stores/hrEmployeeStore";
import { Role } from "~/api/types/enums/role.enum";
import PageToolbar from "~/components/page-toolbar/PageToolbar.vue";
import type {
  HrCreateEmployeeDTO,
  HrUpdateEmployeeDTO,
  HrEmployeeWithAccountSummaryDTO,
} from "~/api/hr_admin/employees/dto";
import type { SelectOptionDTO } from "~/api/types/common/select-option.type";
import type { ColumnConfig } from "~/components/types/tableEdit";
import SummaryCardGrid from "~/components/summary/SummaryCardGrid.vue";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
definePageMeta({ layout: "default" });

const router = useRouter();
const employeeStore = useHrEmployeeStore();
const hrms = hrmsAdminService();
const workingScheduleService = hrms.workingSchedule;
const workLocationService = hrms.workLocation;

const loading = ref(false);
const hasFetchedOnce = ref(false);
const onboardVisible = ref(false);
const actionLoadingById = ref<Record<string, boolean>>({});
const assignmentVisible = ref(false);
const assignmentSaving = ref(false);
const assignmentOptionsLoading = ref(false);
const scheduleOptions = ref<SelectOptionDTO[]>([]);
const workLocationOptions = ref<SelectOptionDTO[]>([]);

const filters = reactive({
  q: "",
  hasAccount: "" as "" | "yes" | "no",
  status: "" as "" | "active" | "inactive",
});

const sourceRows = ref<HrEmployeeWithAccountSummaryDTO[]>([]);
const page = ref(1);
const pageSize = ref(20);

type HrOnboardRole = Role.EMPLOYEE | Role.MANAGER | Role.PAYROLL_MANAGER;

type EmployeeTableRow = {
  id: string;
  employee_code: string;
  full_name: string;
  department: string;
  position: string;
  manager_name: string;
  schedule_name: string;
  work_location_name: string;
  schedule_id: string | null;
  work_location_id: string | null;
  employment_type: string;
  basic_salary: number;
  employee_status: string;
  has_account: boolean;
  account_status: string;
  account_meta: string;
  deleted_at: string | null;
  raw: HrEmployeeWithAccountSummaryDTO;
};

const assignmentForm = reactive<{
  employee_id: string;
  employee_name: string;
  schedule_id: string | null;
  work_location_id: string | null;
}>({
  employee_id: "",
  employee_name: "",
  schedule_id: null,
  work_location_id: null,
});

const isDirty = computed(() => {
  return Boolean(filters.q || filters.hasAccount || filters.status);
});

const filteredSourceRows = computed(() => {
  const q = filters.q.trim().toLowerCase();
  return sourceRows.value.filter((row) => {
    const employee = row.employee;
    const account = row.account ?? row.user ?? null;

    const accountOk =
      filters.hasAccount === ""
        ? true
        : filters.hasAccount === "yes"
        ? Boolean(account)
        : !account;

    const statusOk =
      filters.status === ""
        ? true
        : String(employee.status || "").toLowerCase() === filters.status;

    const qOk =
      !q ||
      [
        employee.employee_code,
        employee.full_name,
        employee.department || "",
        employee.position || "",
        employee.manager_name || "",
        employee.schedule_name || "",
        employee.work_location_name || "",
        account?.email || "",
        account?.username || "",
      ]
        .join(" ")
        .toLowerCase()
        .includes(q);

    return accountOk && statusOk && qOk;
  });
});

const filteredRows = computed<EmployeeTableRow[]>(() => {
  return filteredSourceRows.value.map((row) => {
    const employee = row.employee;
    const account = row.account ?? row.user ?? null;
    return {
      id: employee.id,
      employee_code: employee.employee_code || "-",
      full_name: employee.full_name || "-",
      department: employee.department || "-",
      position: employee.position || "-",
      manager_name: displayRelation(
        employee.manager_name,
        employee.manager_user_id,
      ),
      schedule_name: displayRelation(employee.schedule_name, employee.schedule_id),
      work_location_name: displayRelation(
        employee.work_location_name,
        employee.work_location_id,
      ),
      schedule_id: employee.schedule_id ?? null,
      work_location_id: employee.work_location_id ?? null,
      employment_type: employee.employment_type || "-",
      basic_salary: Number(employee.basic_salary || 0),
      employee_status: employee.status || "unknown",
      has_account: Boolean(account),
      account_status: account?.status || (account ? "linked" : "not linked"),
      account_meta: displayRelation(
        account?.email || account?.username || account?.account_name,
        account?.id,
        "",
      ),
      deleted_at: employee.lifecycle?.deleted_at || null,
      raw: row,
    };
  });
});

const pagedRows = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  return filteredRows.value.slice(start, start + pageSize.value);
});

const stats = computed(() => {
  const total = filteredRows.value.length;
  const active = filteredRows.value.filter(
    (r) => String(r.employee_status || "").toLowerCase() === "active",
  ).length;
  const linked = filteredRows.value.filter((r) => r.has_account).length;
  const noAccount = total - linked;

  return [
    {
      label: "Employees",
      value: total,
      helper: "Directory",
      tone: "primary" as const,
    },
    {
      label: "Active",
      value: active,
      helper: "Current workforce",
      tone: "success" as const,
    },
    {
      label: "Linked Account",
      value: linked,
      helper: "Can login",
      tone: "default" as const,
    },
    {
      label: "No Account",
      value: noAccount,
      helper: "Needs action",
      tone: "warning" as const,
    },
  ];
});
const columns: ColumnConfig<EmployeeTableRow>[] = [
  {
    field: "employee_code",
    label: "Code",
    minWidth: "120px",
    useSlot: true,
    slotName: "employee_code",
  },
  {
    field: "full_name",
    label: "Full Name",
    minWidth: "180px",
    useSlot: true,
    slotName: "full_name",
  },
  {
    field: "department",
    label: "Department",
    minWidth: "140px",
    useSlot: true,
    slotName: "department",
  },
  {
    field: "position",
    label: "Position",
    minWidth: "140px",
    useSlot: true,
    slotName: "position",
  },
  {
    field: "manager_name",
    label: "Manager",
    minWidth: "160px",
    useSlot: true,
    slotName: "manager_name",
  },
  {
    field: "schedule_name",
    label: "Schedule",
    minWidth: "160px",
    useSlot: true,
    slotName: "schedule_name",
  },
  {
    field: "work_location_name",
    label: "Work Location",
    minWidth: "180px",
    useSlot: true,
    slotName: "work_location_name",
  },
  {
    field: "employment_type",
    label: "Type",
    width: "120px",
    useSlot: true,
    slotName: "employment_type",
  },
  {
    field: "basic_salary",
    label: "Basic Salary",
    width: "140px",
    useSlot: true,
    slotName: "basic_salary",
    align: "right",
  },
  {
    field: "employee_status",
    label: "Status",
    width: "120px",
    useSlot: true,
    slotName: "employee_status",
  },
  {
    field: "account_status",
    label: "Account",
    minWidth: "180px",
    useSlot: true,
    slotName: "account_status",
  },
  {
    field: "id",
    label: "Actions",
    operation: true,
    useSlot: true,
    slotName: "operation",
    fixed: "right",
    minWidth: "280px",
  },
];

async function fetchEmployees() {
  loading.value = true;
  try {
    const res = await employeeStore.getEmployeesWithAccounts({
      page: 1,
      limit: 400,
      include_deleted: false,
      with_accounts: true,
    });

    sourceRows.value = res.items ?? [];
    hasFetchedOnce.value = true;

    const maxPage = Math.max(
      1,
      Math.ceil(filteredSourceRows.value.length / pageSize.value),
    );
    if (page.value > maxPage) page.value = maxPage;
  } catch (error) {
    const message =
      (
        error as {
          response?: { data?: { user_message?: string; message?: string } };
        }
      )?.response?.data?.user_message ||
      (
        error as {
          response?: { data?: { user_message?: string; message?: string } };
        }
      )?.response?.data?.message ||
      (error as Error)?.message ||
      "Failed to load employees";
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.q = "";
  filters.hasAccount = "";
  filters.status = "";
  page.value = 1;
}

function goDetail(row: EmployeeTableRow) {
  router.push(ROUTES.HR_ADMIN.EMPLOYEE_DETAIL(row.id));
}

async function loadAssignmentOptions() {
  assignmentOptionsLoading.value = true;
  try {
    const [schedules, locations] = await Promise.all([
      workingScheduleService.getScheduleSelectOptions({ showError: false }),
      workLocationService.getWorkLocationSelectOptions({ showError: false }),
    ]);
    scheduleOptions.value = schedules;
    workLocationOptions.value = locations;
  } finally {
    assignmentOptionsLoading.value = false;
  }
}

function openAssignDialog(row: EmployeeTableRow) {
  assignmentForm.employee_id = row.id;
  assignmentForm.employee_name = row.full_name;
  assignmentForm.schedule_id = row.schedule_id;
  assignmentForm.work_location_id = row.work_location_id;
  assignmentVisible.value = true;

  if (!scheduleOptions.value.length || !workLocationOptions.value.length) {
    void loadAssignmentOptions();
  }
}

function closeAssignDialog() {
  assignmentVisible.value = false;
  assignmentForm.employee_id = "";
  assignmentForm.employee_name = "";
  assignmentForm.schedule_id = null;
  assignmentForm.work_location_id = null;
}

async function submitAssignment() {
  if (!assignmentForm.employee_id) return;

  assignmentSaving.value = true;
  try {
    const payload: HrUpdateEmployeeDTO = {
      schedule_id: assignmentForm.schedule_id || null,
      work_location_id: assignmentForm.work_location_id || null,
    };

    await employeeStore.updateEmployee(assignmentForm.employee_id, payload, {
      showSuccess: false,
    });

    ElMessage.success("Employee assignment updated");
    closeAssignDialog();
    await fetchEmployees();
  } catch (error) {
    ElMessage.error(
      (
        error as {
          response?: { data?: { user_message?: string; message?: string } };
        }
      )?.response?.data?.user_message ||
        (
          error as {
            response?: { data?: { user_message?: string; message?: string } };
          }
        )?.response?.data?.message ||
        (error as Error)?.message ||
        "Failed to update assignment",
    );
  } finally {
    assignmentSaving.value = false;
  }
}

async function confirmDeleteEmployee(fullName: string) {
  await ElMessageBox.confirm(`Delete employee ${fullName}?`, "Confirm Delete", {
    type: "warning",
    confirmButtonText: "Delete",
    cancelButtonText: "Cancel",
  });
}

async function deleteEmployee(row: EmployeeTableRow) {
  const id = row.id;

  try {
    await confirmDeleteEmployee(row.full_name);
  } catch (error) {
    if (error === "cancel" || error === "close") return;
    throw error;
  }

  actionLoadingById.value[id] = true;

  try {
    await employeeStore.softDeleteEmployee(id);
    await fetchEmployees();
  } finally {
    actionLoadingById.value[id] = false;
  }
}
async function restoreEmployee(row: EmployeeTableRow) {
  const id = row.id;
  try {
    actionLoadingById.value[id] = true;
    await employeeStore.restoreEmployee(id);
    ElMessage.success("Employee restored");
    await fetchEmployees();
  } catch (error) {
    ElMessage.error(
      (
        error as {
          response?: { data?: { user_message?: string; message?: string } };
        }
      )?.response?.data?.user_message ||
        (
          error as {
            response?: { data?: { user_message?: string; message?: string } };
          }
        )?.response?.data?.message ||
        (error as Error)?.message ||
        "Failed to restore employee",
    );
  } finally {
    actionLoadingById.value[id] = false;
  }
}

async function submitOnboard(payload: {
  employee: HrCreateEmployeeDTO;
  account: {
    email: string;
    password: string;
    username?: string;
    role?: HrOnboardRole;
  };
}) {
  loading.value = true;

  try {
    await employeeStore.onboardEmployee({
      employee: payload.employee,
      email: payload.account.email,
      password: payload.account.password,
      username: payload.account.username,
      role: String(payload.account.role || Role.EMPLOYEE),
    });

    onboardVisible.value = false;
    await fetchEmployees();
  } finally {
    loading.value = false;
  }
}

watch(
  () => [filters.q, filters.hasAccount, filters.status, pageSize.value],
  () => {
    page.value = 1;
  },
);

onMounted(() => {
  void fetchEmployees();
});
</script>

<template>
  <div class="hr-employee-page">
    <OverviewHeader
      title="HR Employee Directory"
      description="Manage employees and account onboarding with a single clean workflow."
      :backPath="ROUTES.HR_ADMIN.EMPLOYEES"
    >
      <template #actions>
        <BaseButton
          type="primary"
          :loading="loading"
          @click="onboardVisible = true"
        >
          Onboard Employee
        </BaseButton>
      </template>
    </OverviewHeader>
    <PageToolbar class="page-tool-bar">
      <template #left>
        <ElInput
          v-model="filters.q"
          clearable
          placeholder="Search by code, name, department, account..."
          class="toolbar-search"
        />
      </template>

      <template #right>
        <BaseButton
          plain
          @click="router.push(ROUTES.HR_ADMIN.EMPLOYEE_ARCHIVED)"
        >
          Archived
        </BaseButton>

        <BaseButton
          plain
          @click="router.push(ROUTES.HR_ADMIN.EMPLOYEE_ACCOUNTS)"
        >
          Accounts
        </BaseButton>

        <ElSelect v-model="filters.hasAccount" class="toolbar-select">
          <ElOption label="All Accounts" value="" />
          <ElOption label="Has Account" value="yes" />
          <ElOption label="No Account" value="no" />
        </ElSelect>

        <ElSelect v-model="filters.status" class="toolbar-select">
          <ElOption label="All Status" value="" />
          <ElOption label="Active" value="active" />
          <ElOption label="Inactive" value="inactive" />
        </ElSelect>

        <BaseButton plain :disabled="!isDirty" @click="resetFilters">
          Reset
        </BaseButton>
      </template>
    </PageToolbar>
    <SummaryCardGrid :items="stats" :columns="4" elevated />
    <ElCard class="table-shell">
      <SmartTable
        :data="pagedRows"
        :columns="columns"
        :loading="loading"
        :has-fetched-once="hasFetchedOnce"
      >
        <template #employee_code="{ row }">
          {{ row.employee_code }}
        </template>

        <template #full_name="{ row }">
          {{ row.full_name }}
        </template>

        <template #department="{ row }">
          {{ row.department }}
        </template>

        <template #position="{ row }">
          {{ row.position }}
        </template>

        <template #manager_name="{ row }">
          {{ row.manager_name }}
        </template>

        <template #schedule_name="{ row }">
          {{ row.schedule_name }}
        </template>

        <template #work_location_name="{ row }">
          {{ row.work_location_name }}
        </template>

        <template #employment_type="{ row }">
          <ElTag effect="plain">{{ row.employment_type }}</ElTag>
        </template>

        <template #basic_salary="{ row }">
          {{
            Number(row.basic_salary || 0).toLocaleString("en-US", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })
          }}
        </template>

        <template #employee_status="{ row }">
          <ElTag
            :type="row.employee_status === 'active' ? 'success' : 'warning'"
            effect="plain"
          >
            {{ row.employee_status }}
          </ElTag>
        </template>

        <template #account_status="{ row }">
          <div class="account-cell">
            <ElTag :type="row.has_account ? 'success' : 'info'" effect="plain">
              {{ row.account_status }}
            </ElTag>
            <small v-if="row.has_account" class="account-meta">
              {{ row.account_meta }}
            </small>
          </div>
        </template>

        <template #operation="{ row }">
          <EmployeeRowActions
            :row="{
              id: row.id,
              full_name: row.full_name,
              deleted_at: row.deleted_at,
            }"
            :loading="actionLoadingById[row.id]"
            @detail="goDetail(row)"
            @assign-schedule="openAssignDialog(row)"
            @delete="deleteEmployee(row)"
            @restore="restoreEmployee(row)"
          />
        </template>
      </SmartTable>

      <div class="pagination-wrap">
        <ElPagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          background
          layout="total, sizes, prev, pager, next"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredRows.length"
        />
      </div>
    </ElCard>

    <EmployeeOnboardDialog
      v-model:visible="onboardVisible"
      :loading="loading"
      @submitted="submitOnboard"
    />

    <ElDialog
      v-model="assignmentVisible"
      width="520px"
      title="Assign Schedule & Location"
      :close-on-click-modal="false"
      @closed="closeAssignDialog"
    >
      <ElForm label-position="top">
        <ElFormItem label="Employee">
          <ElInput :model-value="assignmentForm.employee_name" disabled />
        </ElFormItem>

        <ElFormItem label="Working Schedule">
          <ElSelect
            v-model="assignmentForm.schedule_id"
            clearable
            filterable
            placeholder="Select schedule"
            :loading="assignmentOptionsLoading"
          >
            <ElOption
              v-for="item in scheduleOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </ElSelect>
        </ElFormItem>

        <ElFormItem label="Work Location">
          <ElSelect
            v-model="assignmentForm.work_location_id"
            clearable
            filterable
            placeholder="Select work location"
            :loading="assignmentOptionsLoading"
          >
            <ElOption
              v-for="item in workLocationOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </ElSelect>
        </ElFormItem>
      </ElForm>

      <template #footer>
        <div class="assignment-actions">
          <BaseButton plain :disabled="assignmentSaving" @click="closeAssignDialog">
            Cancel
          </BaseButton>
          <BaseButton
            type="primary"
            :loading="assignmentSaving"
            @click="submitAssignment"
          >
            Save Assignment
          </BaseButton>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.hr-employee-page {
  padding: 16px;
  max-width: 1460px;
  margin: 0 auto;
  color: var(--text-color, var(--el-text-color-primary));
}

.table-shell {
  margin-top: 12px;
  border: 1px solid var(--border-color);
  background: var(--color-card);
  box-shadow: var(--shadow-sm, 0 6px 16px rgba(16, 24, 40, 0.05));
}

.page-tool-bar {
  margin-block: 12px;
}

.toolbar-search {
  min-width: min(460px, 100%);
}

.toolbar-select {
  min-width: 140px;
}

.account-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.account-meta {
  color: var(--muted-color);
  font-size: 12px;
  line-height: 1.35;
  word-break: break-word;
}

.pagination-wrap {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.assignment-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 780px) {
  .pagination-wrap {
    justify-content: flex-start;
  }

  .assignment-actions {
    justify-content: stretch;
  }

  .assignment-actions :deep(.el-button),
  .assignment-actions :deep(button) {
    width: 100%;
  }
}
</style>
