<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
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
  ElRow,
  ElSelect,
  ElTag,
} from "element-plus";

import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import PageToolbar from "~/components/page-toolbar/PageToolbar.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";

import type {
  HrCreateEmployeeAccountDTO,
  HrEmployeeAccountListItemDTO,
  HrEmployeeDTO,
  HrEmployeeWithAccountSummaryDTO,
} from "~/api/hr_admin/employees/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import {
  buildAccountOptionLabel,
  normalizeAccountRole,
} from "~/api/hr_admin/employees/accountOptions";
import { ROUTES } from "~/constants/routes";
import { Status } from "~/api/types/enums/status.enum";
import { Role } from "~/api/types/enums/role.enum";
import { useHrEmployeeStore } from "~/stores/hrEmployeeStore";

definePageMeta({ layout: "default" });

type AccountRoleFilter = "all" | "employee" | "manager" | "payroll_manager";
type AccountStatusValue = `${Status}`;

interface AccountTableRow {
  id: string;
  employee_id: string;
  user_id: string | null;
  employee_name: string;
  account_name: string;
  account_email?: string | null;
  is_linked?: boolean;
  email?: string | null;
  username?: string | null;
  role?: string | null;
  status?: string | null;
  account_deleted: boolean;
}

const router = useRouter();
const employeeStore = useHrEmployeeStore();

const rows = ref<AccountTableRow[]>([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const totalRows = ref(0);
const search = ref("");
const roleFilter = ref<AccountRoleFilter>("all");

const deleteAccountSaving = ref<Record<string, boolean>>({});
const restoreAccountSaving = ref<Record<string, boolean>>({});
const updateStatusSaving = ref<Record<string, boolean>>({});

const createDialogVisible = ref(false);
const createSaving = ref(false);
const createCandidatesLoading = ref(false);
const createCandidates = ref<HrEmployeeDTO[]>([]);
const createForm = reactive<{
  employee_id: string;
  email: string;
  username: string;
  password: string;
  role: Role;
}>({
  employee_id: "",
  email: "",
  username: "",
  password: "",
  role: Role.EMPLOYEE,
});

const tableColumns: ColumnConfig<AccountTableRow>[] = [
  { field: "username", label: "Username", minWidth: "180px" },
  { field: "employee_name", label: "Employee", minWidth: "220px" },
  { field: "account_name", label: "Account", minWidth: "220px" },
  { field: "email", label: "Email", minWidth: "260px" },
  {
    field: "role",
    label: "Role",
    width: "140px",
    useSlot: true,
    slotName: "role",
  },
  {
    field: "status",
    label: "Status",
    width: "130px",
    useSlot: true,
    slotName: "status",
  },
  {
    field: "id",
    label: "Actions",
    operation: true,
    minWidth: "360px",
    useSlot: true,
    slotName: "operation",
    fixed: "right",
  },
];

function roleAllowed(role: string) {
  if (roleFilter.value === "all") {
    return (
      role === "employee" || role === "manager" || role === "payroll_manager"
    );
  }
  return role === roleFilter.value;
}

function toManagerAccountRow(
  item: HrEmployeeWithAccountSummaryDTO,
): AccountTableRow | null {
  const account = item.account ?? item.user ?? null;
  if (!account) return null;

  const employeeId = String(item.employee.id ?? "").trim();
  if (!employeeId) return null;

  const userId = String(account.user_id ?? "").trim() || null;

  const role = normalizeAccountRole(account.role);
  if (!roleAllowed(role)) return null;

  const accountRecord = account as unknown as Record<string, unknown>;
  const lifecycle = accountRecord.lifecycle as
    | Record<string, unknown>
    | undefined;
  const deletedAt =
    (accountRecord.deleted_at as string | null | undefined) ??
    (lifecycle?.deleted_at as string | null | undefined) ??
    null;

  return {
    id: employeeId,
    employee_id: employeeId,
    user_id: userId,
    employee_name: displayRelation(
      item.employee.employee_name ?? item.employee.full_name,
      employeeId,
    ),
    account_name: buildAccountOptionLabel(
      account as HrEmployeeAccountListItemDTO,
      "Account",
    ),
    account_email: account.account_email ?? account.email ?? null,
    email: account.account_email ?? account.email ?? null,
    username: account.username ?? null,
    role,
    status: account.status ?? null,
    is_linked: !!item.employee,
    account_deleted: !!deletedAt,
  };
}

function employeeActionKey(row: AccountTableRow): string {
  return String(row.employee_id || row.id);
}

function userActionKey(row: AccountTableRow): string {
  return String(row.user_id ?? "").trim();
}

function requireUserTargetId(row: AccountTableRow): string | null {
  const userId = userActionKey(row);
  if (userId) return userId;

  ElMessage.warning(
    `Missing linked account id for ${displayRelation(
      row.employee_name,
      row.employee_id,
    )}`,
  );
  return null;
}

// HRMS account routes are mixed-scope:
// - soft-delete / restore are employee-scoped
// - status update is IAM user-scoped
// Keep both IDs on each row and route them explicitly.

async function fetchManagerAccounts(page = currentPage.value) {
  loading.value = true;
  try {
    const res = await employeeStore.getEmployeesWithAccounts({
      page,
      limit: pageSize.value,
      q: search.value.trim() || undefined,
      include_deleted: true,
      with_accounts: true,
    });

    rows.value = (res.items ?? [])
      .map(toManagerAccountRow)
      .filter((row): row is AccountTableRow => !!row);

    totalRows.value = rows.value.length;
    currentPage.value = page;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loading.value = false;
  }
}

function resetCreateForm() {
  createForm.employee_id = "";
  createForm.email = "";
  createForm.username = "";
  createForm.password = "";
  createForm.role = Role.EMPLOYEE;
}

async function fetchCreateCandidates(keyword = "") {
  createCandidatesLoading.value = true;
  try {
    const res = await employeeStore.getEmployeesWithAccounts({
      page: 1,
      limit: 200,
      q: keyword.trim() || undefined,
      with_accounts: true,
    });

    createCandidates.value = (res.items ?? [])
      .filter((item) => !(item.account ?? item.user))
      .map((item) => item.employee);
  } catch {
    // API notifications are handled by service layer
  } finally {
    createCandidatesLoading.value = false;
  }
}

async function openCreateDialog() {
  resetCreateForm();
  createDialogVisible.value = true;
  await fetchCreateCandidates();
}

function closeCreateDialog() {
  createDialogVisible.value = false;
  resetCreateForm();
}

async function submitCreateAccount() {
  if (!createForm.employee_id) {
    ElMessage.error("Please select an employee");
    return;
  }
  if (!createForm.email.trim()) {
    ElMessage.error("Email is required");
    return;
  }
  if (!createForm.password || createForm.password.length < 6) {
    ElMessage.error("Password must be at least 6 characters");
    return;
  }

  const payload: HrCreateEmployeeAccountDTO = {
    email: createForm.email.trim(),
    username: createForm.username.trim() || undefined,
    password: createForm.password,
    role: createForm.role,
  };

  createSaving.value = true;
  try {
    await employeeStore.createAccount(createForm.employee_id, payload);
    closeCreateDialog();
    await fetchManagerAccounts(currentPage.value);
  } catch {
    // API notifications are handled by service layer
  } finally {
    createSaving.value = false;
  }
}

async function handleDeleteAccount(row: AccountTableRow) {
  try {
    await ElMessageBox.confirm(
      `Delete account for ${displayRelation(
        row.employee_name,
        row.employee_id,
      )}?`,
      "Confirm Delete Account",
      {
        type: "warning",
        confirmButtonText: "Delete",
        cancelButtonText: "Cancel",
      },
    );

    const targetEmployeeId = employeeActionKey(row);
    const rowId = targetEmployeeId;
    deleteAccountSaving.value[rowId] = true;
    await employeeStore.softDeleteEmployeeAccount(targetEmployeeId);
    await fetchManagerAccounts(currentPage.value);
  } catch (error: any) {
    if (error === "cancel" || error === "close") return;
  } finally {
    deleteAccountSaving.value[employeeActionKey(row)] = false;
  }
}

async function handleRestoreAccount(row: AccountTableRow) {
  try {
    await ElMessageBox.confirm(
      `Restore account for ${displayRelation(
        row.employee_name,
        row.employee_id,
      )}?`,
      "Confirm Restore Account",
      {
        type: "info",
        confirmButtonText: "Restore",
        cancelButtonText: "Cancel",
      },
    );

    const targetEmployeeId = employeeActionKey(row);
    const rowId = targetEmployeeId;
    restoreAccountSaving.value[rowId] = true;
    await employeeStore.restoreEmployeeAccount(targetEmployeeId);
    await fetchManagerAccounts(currentPage.value);
  } catch (error: any) {
    if (error === "cancel" || error === "close") return;
  } finally {
    restoreAccountSaving.value[employeeActionKey(row)] = false;
  }
}

async function handleSetAccountStatus(
  row: AccountTableRow,
  status: AccountStatusValue,
) {
  if (!status) return;

  const previous = String(row.status ?? Status.ACTIVE);
  if (previous === status) return;

  const targetUserId = requireUserTargetId(row);
  if (!targetUserId) return;

  const rowId = targetUserId;
  updateStatusSaving.value[rowId] = true;

  try {
    await employeeStore.setEmployeeAccountStatus(targetUserId, {
      status: status as Status,
    });
    row.status = status;
  } catch {
    row.status = previous;
  } finally {
    updateStatusSaving.value[rowId] = false;
  }
}

async function handleSearch() {
  currentPage.value = 1;
  await fetchManagerAccounts(1);
}

function resetFilters() {
  search.value = "";
  roleFilter.value = "all";
  void fetchManagerAccounts(1);
}

onMounted(async () => {
  await fetchManagerAccounts(1);
});
</script>

<template>
  <div class="hr-employee-page">
    <OverviewHeader
      title="Employee Accounts"
      description="Manage employee accounts, status, and onboarding with a clean workflow."
      :backPath="ROUTES.HR_ADMIN.EMPLOYEES"
    >
      <template #actions>
        <BaseButton type="primary" :loading="loading" @click="openCreateDialog">
          Create Employee Account
        </BaseButton>
      </template>
    </OverviewHeader>

    <PageToolbar class="page-tool-bar">
      <template #left>
        <ElInput
          v-model="search"
          clearable
          placeholder="Search by name, username, email"
          class="toolbar-search"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
      </template>

      <template #right>
        <ElSelect
          v-model="roleFilter"
          class="toolbar-select"
          @change="handleSearch"
        >
          <ElOption label="All Roles" value="all" />
          <ElOption label="Employee" value="employee" />
          <ElOption label="Manager" value="manager" />
          <ElOption label="Payroll Manager" value="payroll_manager" />
        </ElSelect>

        <BaseButton plain @click="handleSearch">Refresh</BaseButton>
        <BaseButton
          plain
          @click="resetFilters"
          :disabled="!search && roleFilter === 'all'"
        >
          Reset
        </BaseButton>
      </template>
    </PageToolbar>

    <ElCard class="table-shell" shadow="never">
      <SmartTable
        :data="rows"
        :columns="tableColumns"
        :loading="loading"
        :total="totalRows"
        :page="currentPage"
        :page-size="pageSize"
        :has-fetched-once="true"
        @page="fetchManagerAccounts"
      >
        <template #role="{ row }">
          <ElTag
            :type="row.role === 'payroll_manager' ? 'warning' : 'primary'"
            effect="plain"
          >
            {{ row.role || "-" }}
          </ElTag>
        </template>

        <template #status="{ row }">
          <ElTag
            :type="
              (row.status ?? Status.ACTIVE) === Status.ACTIVE
                ? 'success'
                : (row.status ?? Status.ACTIVE) === Status.INACTIVE
                ? 'warning'
                : 'danger'
            "
            effect="plain"
            size="small"
          >
            {{ row.status || "-" }}
          </ElTag>
        </template>

        <template #operation="{ row }">
          <div class="operation-actions">
            <ElSelect
              :model-value="String(row.status || Status.ACTIVE)"
              size="small"
              style="width: 132px"
              :disabled="!row.user_id || (updateStatusSaving?.[userActionKey(row)] ?? false)"
              @change="(value) => handleSetAccountStatus(row, value as AccountStatusValue)"
            >
              <ElOption label="Active" :value="Status.ACTIVE" />
              <ElOption label="Inactive" :value="Status.INACTIVE" />
              <ElOption label="Suspended" :value="Status.SUSPENDED" />
            </ElSelect>

            <BaseButton
              v-if="!row.account_deleted"
              size="small"
              type="danger"
              plain
              :loading="deleteAccountSaving?.[employeeActionKey(row)] ?? false"
              @click="handleDeleteAccount(row)"
            >
              Delete
            </BaseButton>
            <BaseButton
              v-else
              size="small"
              type="success"
              plain
              :loading="restoreAccountSaving?.[employeeActionKey(row)] ?? false"
              @click="handleRestoreAccount(row)"
            >
              Restore
            </BaseButton>
          </div>
        </template>
      </SmartTable>

      <ElRow v-if="totalRows > 0" justify="end" class="mt-6">
        <ElPagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="totalRows"
          layout="total, prev, pager, next, jumper"
          @current-change="fetchManagerAccounts"
        />
      </ElRow>
    </ElCard>

    <ElDialog
      v-model="createDialogVisible"
      title="Create Employee Account"
      width="640px"
      @close="closeCreateDialog"
    >
      <ElForm label-position="top">
        <ElFormItem label="Employee">
          <ElSelect
            v-model="createForm.employee_id"
            filterable
            clearable
            :loading="createCandidatesLoading"
            placeholder="Select employee without account"
            style="width: 100%"
          >
            <ElOption
              v-for="employee in createCandidates"
              :key="employee.id"
              :label="`${employee.employee_code} - ${employee.full_name}`"
              :value="employee.id"
            />
          </ElSelect>
        </ElFormItem>

        <ElFormItem label="Email">
          <ElInput
            v-model="createForm.email"
            placeholder="employee@company.com"
            clearable
          />
        </ElFormItem>

        <ElFormItem label="Username">
          <ElInput
            v-model="createForm.username"
            placeholder="Optional username"
            clearable
          />
        </ElFormItem>

        <ElFormItem label="Password">
          <ElInput
            v-model="createForm.password"
            type="password"
            show-password
            placeholder="At least 6 characters"
          />
        </ElFormItem>

        <ElFormItem label="Role">
          <ElSelect v-model="createForm.role" style="width: 100%">
            <ElOption label="Employee" :value="Role.EMPLOYEE" />
            <ElOption label="Manager" :value="Role.MANAGER" />
            <ElOption label="Payroll Manager" :value="Role.PAYROLL_MANAGER" />
          </ElSelect>
        </ElFormItem>
      </ElForm>

      <template #footer>
        <div class="dialog-actions">
          <BaseButton @click="closeCreateDialog">Cancel</BaseButton>
          <BaseButton
            type="primary"
            :loading="createSaving"
            @click="submitCreateAccount"
          >
            Create Account
          </BaseButton>
        </div>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.operation-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.toolbar-search {
  min-width: 280px;
  max-width: 100%;
}

.toolbar-select {
  min-width: 170px;
}

.page-tool-bar {
  gap: 10px;
}

.hr-employee-page {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1460px;
  margin: 0 auto;
  color: var(--text-color, var(--el-text-color-primary));
}

.table-shell {
  border: 1px solid var(--border-color);
  background: var(--color-card);
  box-shadow: var(--shadow-sm, 0 6px 16px rgba(16, 24, 40, 0.05));
}
</style>
