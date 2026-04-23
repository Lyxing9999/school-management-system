<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { CopyDocument, Refresh, UserFilled } from "@element-plus/icons-vue";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  HrEmployeeDTO,
  HrUpdateEmployeeAccountDTO,
  HrUpdateEmployeeDTO,
  HrSalaryType,
} from "~/api/hr_admin/employees/dto";
import type { SelectOptionDTO } from "~/api/types/common/select-option.type";
import { useHrEmployeeStore } from "~/stores/hrEmployeeStore";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import {
  toAccountSelectOption,
  toManagerSelectOptions,
} from "~/api/hr_admin/employees/accountOptions";


definePageMeta({ layout: "default" });

type EmploymentType = "permanent" | "contract";
type EmployeeStatus = "active" | "inactive";

type AccountSummary = {
  id: string;
  email?: string | null;
  username?: string | null;
  role?: string | null;
  status?: string | null;
} | null;

type EmployeeContractForm = {
  start_date: string;
  end_date: string;
  salary_type: HrSalaryType;
  rate: number | null;
  pay_on_holiday: boolean;
  pay_on_weekend: boolean;
  leave_policy_id: string | null;
};

type EmployeeForm = {
  full_name: string;
  department: string;
  position: string;
  manager_user_id: string | null;
  work_location_id: string | null;
  employment_type: EmploymentType;
  basic_salary: number | null;
  status: EmployeeStatus;
  contract: EmployeeContractForm | null;
};

type AccountForm = {
  email: string;
  username: string;
  password: string;
};

const route = useRoute();
const router = useRouter();

const employeeStore = useHrEmployeeStore();
const scheduleService = hrmsAdminService().workingSchedule;
const workLocationService = hrmsAdminService().workLocation;
const { $api } = useNuxtApp();

const employeeId = computed(() => String(route.params.id ?? ""));

const pageLoading = ref(false);
const employeeSaving = ref(false);
const accountSaving = ref(false);
const assignSaving = ref(false);
const linkSaving = ref(false);
const resetSaving = ref(false);
const defaultResetSaving = ref(false);

const scheduleOptionsLoading = ref(false);
const locationOptionsLoading = ref(false);
const accountOptionsLoading = ref(false);
const managerOptionsLoading = ref(false);

const employee = ref<HrEmployeeDTO | null>(null);
const account = ref<AccountSummary>(null);
const resetInfo = ref<{ message?: string; reset_link?: string } | null>(null);

const scheduleOptions = ref<SelectOptionDTO[]>([]);
const locationOptions = ref<SelectOptionDTO[]>([]);
const managerOptions = ref<Array<{ value: string; label: string }>>([]);
const accountOptions = ref<Array<{ value: string; label: string }>>([]);

const employeeForm = reactive<EmployeeForm>(createEmptyEmployeeForm());
const accountForm = reactive<AccountForm>(createEmptyAccountForm());

const assignForm = reactive({
  schedule_id: "",
});

const linkForm = reactive({
  user_id: "",
});

function createEmptyContract(): EmployeeContractForm {
  return {
    start_date: "",
    end_date: "",
    salary_type: "monthly",
    rate: null,
    pay_on_holiday: false,
    pay_on_weekend: false,
    leave_policy_id: null,
  };
}

function createEmptyEmployeeForm(): EmployeeForm {
  return {
    full_name: "",
    department: "",
    position: "",
    manager_user_id: null,
    work_location_id: null,
    employment_type: "permanent",
    basic_salary: null,
    status: "active",
    contract: null,
  };
}

function createEmptyAccountForm(): AccountForm {
  return {
    email: "",
    username: "",
    password: "",
  };
}

watch(
  () => employeeForm.employment_type,
  (type) => {
    if (type === "contract" && !employeeForm.contract) {
      employeeForm.contract = createEmptyContract();
      return;
    }

    if (type === "permanent") {
      employeeForm.contract = null;
    }
  },
);

function notifyError(error: unknown, fallback: string) {
  ElMessage.error(mapError(error, fallback));
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

function formatCurrency(value: number | null | undefined) {
  if (value == null) return "-";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

function fillEmployeeForm(data: HrEmployeeDTO) {
  employeeForm.full_name = data.full_name ?? "";
  employeeForm.department = data.department ?? "";
  employeeForm.position = data.position ?? "";
  employeeForm.manager_user_id = data.manager_user_id ?? null;
  employeeForm.work_location_id = data.work_location_id ?? null;
  employeeForm.employment_type =
    data.employment_type === "contract" ? "contract" : "permanent";
  employeeForm.basic_salary = data.basic_salary ?? 0;
  employeeForm.status = data.status === "inactive" ? "inactive" : "active";

  if (data.contract) {
    employeeForm.contract = {
      start_date: data.contract.start_date ?? "",
      end_date: data.contract.end_date ?? "",
      salary_type: data.contract.salary_type ?? "monthly",
      rate: data.contract.rate ?? null,
      pay_on_holiday: data.contract.pay_on_holiday ?? false,
      pay_on_weekend: data.contract.pay_on_weekend ?? false,
      leave_policy_id: data.contract.leave_policy_id ?? null,
    };
  } else {
    employeeForm.contract = null;
  }
}

function fillAccountForm() {
  accountForm.email = account.value?.email ?? "";
  accountForm.username = account.value?.username ?? "";
  accountForm.password = "";
}

function buildEmployeePayload(): HrUpdateEmployeeDTO | null {
  if (!employeeForm.full_name.trim()) {
    ElMessage.warning("Full name is required");
    return null;
  }

  if (
    employeeForm.basic_salary == null ||
    Number(employeeForm.basic_salary) < 0
  ) {
    ElMessage.warning("Basic salary must be 0 or greater");
    return null;
  }

  if (employeeForm.employment_type === "contract") {
    if (!employeeForm.contract?.start_date) {
      ElMessage.warning("Contract start date is required");
      return null;
    }

    if (!employeeForm.contract?.end_date) {
      ElMessage.warning("Contract end date is required");
      return null;
    }

    if (
      employeeForm.contract.rate == null ||
      Number(employeeForm.contract.rate) < 0
    ) {
      ElMessage.warning("Contract rate must be 0 or greater");
      return null;
    }
  }

  return {
    full_name: employeeForm.full_name.trim(),
    department: employeeForm.department.trim() || null,
    position: employeeForm.position.trim() || null,
    manager_user_id: employeeForm.manager_user_id || null,
    work_location_id: employeeForm.work_location_id || null,
    employment_type: employeeForm.employment_type,
    basic_salary: Number(employeeForm.basic_salary),
    status: employeeForm.status,
    contract:
      employeeForm.employment_type === "contract" && employeeForm.contract
        ? {
            start_date: employeeForm.contract.start_date,
            end_date: employeeForm.contract.end_date,
            salary_type: employeeForm.contract.salary_type,
            rate: Number(employeeForm.contract.rate),
            pay_on_holiday: employeeForm.contract.pay_on_holiday,
            pay_on_weekend: employeeForm.contract.pay_on_weekend,
            leave_policy_id: employeeForm.contract.leave_policy_id,
          }
        : null,
  };
}

function buildAccountPayload(): HrUpdateEmployeeAccountDTO | null {
  if (!account.value) return null;

  const payload: HrUpdateEmployeeAccountDTO = {};

  if (accountForm.email.trim()) payload.email = accountForm.email.trim();
  if (accountForm.username.trim())
    payload.username = accountForm.username.trim();
  if (accountForm.password.trim()) payload.password = accountForm.password;

  if (!payload.email && !payload.username && !payload.password) {
    ElMessage.warning("Add at least one account field to update");
    return null;
  }

  return payload;
}

async function loadScheduleOptions() {
  scheduleOptionsLoading.value = true;
  try {
    scheduleOptions.value = await scheduleService.getScheduleSelectOptions({
      showError: false,
    });
  } catch {
    scheduleOptions.value = [];
  } finally {
    scheduleOptionsLoading.value = false;
  }
}

async function loadWorkLocationOptions() {
  locationOptionsLoading.value = true;
  try {
    locationOptions.value = await workLocationService.getWorkLocationSelectOptions(
      { showError: false },
    );
  } catch {
    locationOptions.value = [];
  } finally {
    locationOptionsLoading.value = false;
  }
}

async function loadManagerOptions() {
  managerOptionsLoading.value = true;
  try {
    const response = await employeeStore.getEmployeeAccounts({
      page: 1,
      limit: 500,
      status: "active",
    });

    managerOptions.value = toManagerSelectOptions(response.items ?? []);
  } catch {
    managerOptions.value = [];
  } finally {
    managerOptionsLoading.value = false;
  }
}

async function loadAccountOptions() {
  accountOptionsLoading.value = true;
  try {
    const response = await employeeStore.getEmployeeAccounts({
      page: 1,
      limit: 300,
    });

    accountOptions.value = (response.items ?? [])
      .map((item) => toAccountSelectOption(item, "Account"))
      .filter((item): item is { value: string; label: string } => !!item);
  } catch {
    accountOptions.value = [];
  } finally {
    accountOptionsLoading.value = false;
  }
}

async function loadDetail() {
  if (!employeeId.value) return;

  pageLoading.value = true;
  resetInfo.value = null;

  try {
    const [employeeRes, accountRes] = await Promise.all([
      employeeStore.getEmployee(employeeId.value),
      employeeStore.getEmployeeAccount(employeeId.value),
    ]);

    employee.value = employeeRes;
    account.value = accountRes;
    fillEmployeeForm(employeeRes);
    fillAccountForm();
    assignForm.schedule_id = employeeRes.schedule_id ?? "";

    await Promise.all([
      loadScheduleOptions(),
      loadWorkLocationOptions(),
      loadManagerOptions(),
      loadAccountOptions(),
    ]);

    if (
      employeeRes.manager_user_id &&
      !managerOptions.value.some(
        (option) => option.value === employeeRes.manager_user_id,
      )
    ) {
      managerOptions.value = [
        {
          value: employeeRes.manager_user_id,
          label: displayRelation(
            employeeRes.manager_name,
            employeeRes.manager_user_id,
            "Assigned manager",
          ),
        },
        ...managerOptions.value,
      ];
    }

    if (
      employeeRes.work_location_id &&
      !locationOptions.value.some(
        (option) => option.value === employeeRes.work_location_id,
      )
    ) {
      locationOptions.value = [
        {
          value: employeeRes.work_location_id,
          label: displayRelation(
            employeeRes.work_location_name,
            employeeRes.work_location_id,
            "Current work location",
          ),
        },
        ...locationOptions.value,
      ];
    }

    if (
      employeeRes.schedule_id &&
      !scheduleOptions.value.some(
        (option) => option.value === employeeRes.schedule_id,
      )
    ) {
      scheduleOptions.value = [
        {
          value: employeeRes.schedule_id,
          label: displayRelation(
            employeeRes.schedule_name,
            employeeRes.schedule_id,
            "Current schedule",
          ),
        },
        ...scheduleOptions.value,
      ];
    }
  } catch {
    // API notifications are handled by service layer
  } finally {
    pageLoading.value = false;
  }
}

async function submitEmployeeUpdate() {
  if (!employeeId.value) return;

  const payload = buildEmployeePayload();
  if (!payload) return;

  employeeSaving.value = true;
  try {
    const updated = await employeeStore.updateEmployee(
      employeeId.value,
      payload,
    );
    employee.value = updated;
    fillEmployeeForm(updated);
  } catch {
    // API notifications are handled by service layer
  } finally {
    employeeSaving.value = false;
  }
}

async function submitAccountUpdate() {
  if (!employeeId.value || !account.value) return;

  const payload = buildAccountPayload();
  if (!payload) return;

  accountSaving.value = true;
  try {
    const updated = await employeeStore.updateEmployeeAccount(
      employeeId.value,
      payload,
    );
    account.value = updated;
    fillAccountForm();
  } catch {
    // API notifications are handled by service layer
  } finally {
    accountSaving.value = false;
  }
}

async function submitAssignSchedule() {
  if (!employeeId.value) return;

  if (!assignForm.schedule_id) {
    ElMessage.warning("Please select a schedule");
    return;
  }

  assignSaving.value = true;
  try {
    if (!$api) throw new Error("API client unavailable");

    await ($api as any).post(
      `/api/hrms/employees/${employeeId.value}/assign-schedule`,
      {
        schedule_id: assignForm.schedule_id,
      },
    );

    ElMessage.success("Schedule assigned successfully");
  } catch (error) {
    notifyError(error, "Failed to assign schedule");
  } finally {
    assignSaving.value = false;
  }
}

async function submitLinkAccount() {
  if (!employeeId.value) return;

  if (!linkForm.user_id) {
    ElMessage.warning("Please select an account");
    return;
  }

  linkSaving.value = true;
  try {
    const updated = await employeeStore.linkAccount(employeeId.value, {
      user_id: linkForm.user_id,
    });

    employee.value = updated;
    account.value = await employeeStore.getEmployeeAccount(employeeId.value);
    fillAccountForm();
    linkForm.user_id = "";
  } catch {
    // API notifications are handled by service layer
  } finally {
    linkSaving.value = false;
  }
}

async function requestPasswordReset() {
  if (!employeeId.value) return;

  resetSaving.value = true;
  try {
    const response = await employeeStore.requestEmployeeAccountPasswordReset(
      employeeId.value,
      { showError: false, showSuccess: false },
    );

    resetInfo.value = response;
    ElMessage.success(response.message || "Password reset requested");
  } catch (error) {
    notifyError(error, "Failed to request password reset");
  } finally {
    resetSaving.value = false;
  }
}

async function resetPasswordDefault() {
  if (!employeeId.value) return;

  let newPassword = "";
  try {
    const prompt = await ElMessageBox.prompt(
      "Enter a new password (minimum 6 characters).",
      "Reset Employee Password",
      {
        inputType: "password",
        inputValue: "",
        inputPlaceholder: "New password",
        confirmButtonText: "Reset",
        cancelButtonText: "Cancel",
        inputValidator: (value) => {
          if (!value || value.trim().length < 6) {
            return "Password must be at least 6 characters";
          }
          return true;
        },
      },
    );
    newPassword = String(prompt.value ?? "").trim();
    if (!newPassword) return;
  } catch (error) {
    if (error === "cancel" || error === "close") return;
    notifyError(error, "Failed to collect new password");
    return;
  }

  defaultResetSaving.value = true;
  try {
    if (!$api) throw new Error("API client unavailable");

    await ($api as any).post(
      `/api/hrms/employees/${employeeId.value}/account/reset-password`,
      { new_password: newPassword },
    );

    ElMessage.success("Password reset successfully");
  } catch (error) {
    notifyError(error, "Failed to reset password");
  } finally {
    defaultResetSaving.value = false;
  }
}

async function copyResetLink() {
  const link = resetInfo.value?.reset_link;
  if (!link) return;

  try {
    await navigator.clipboard.writeText(link);
    ElMessage.success("Reset link copied");
  } catch {
    ElMessage.warning("Could not copy link automatically");
  }
}

onMounted(loadDetail);
</script>

<template>
  <div class="employee-detail-page">
    <OverviewHeader
      :title="employee ? employee.full_name : 'Employee Detail'"
      :description="
        employee
          ? `Code: ${employee.employee_code}`
          : 'Loading employee profile and account details'
      "
      @refresh="loadDetail"
    >
      <template #actions>
        <div class="header-actions">
          <BaseButton plain @click="router.push('/hr/employees')">
            Back to Directory
          </BaseButton>
          <BaseButton type="primary" :loading="pageLoading" @click="loadDetail">
            Refresh
          </BaseButton>
        </div>
      </template>
    </OverviewHeader>

    <el-skeleton v-if="pageLoading" :rows="10" animated />

    <template v-else>
      <div class="top-grid">
        <el-card shadow="never" class="profile-card">
          <div class="profile-head">
            <el-avatar :size="48" class="profile-avatar">
              <el-icon><UserFilled /></el-icon>
            </el-avatar>

            <div class="profile-info">
              <div class="profile-name">{{ employee?.full_name || "-" }}</div>
              <div class="profile-meta">
                {{ employee?.employee_code || "-" }}
              </div>
            </div>
          </div>

          <div class="mini-grid">
            <div class="mini-item">
              <span>Employment</span>
              <strong>{{ employee?.employment_type || "-" }}</strong>
            </div>
            <div class="mini-item">
              <span>Status</span>
              <strong>{{ employee?.status || "-" }}</strong>
            </div>
            <div class="mini-item">
              <span>Department</span>
              <strong>{{ employee?.department || "-" }}</strong>
            </div>
            <div class="mini-item">
              <span>Manager</span>
              <strong>{{
                displayRelation(
                  employee?.manager_name,
                  employee?.manager_user_id,
                )
              }}</strong>
            </div>
            <div class="mini-item">
              <span>Location</span>
              <strong>{{
                displayRelation(
                  employee?.work_location_name,
                  employee?.work_location_id,
                )
              }}</strong>
            </div>
            <div class="mini-item">
              <span>Salary</span>
              <strong>{{ formatCurrency(employee?.basic_salary) }}</strong>
            </div>
          </div>
        </el-card>

        <el-card shadow="never" class="profile-card">
          <div class="card-title">Reset Password</div>

          <div class="action-stack">
            <BaseButton
              type="warning"
              :loading="resetSaving"
              :disabled="!account"
              @click="requestPasswordReset"
            >
              Request Reset Link
            </BaseButton>

            <BaseButton
              type="danger"
              plain
              :loading="defaultResetSaving"
              :disabled="!account"
              @click="resetPasswordDefault"
            >
              Reset Password
            </BaseButton>

            <div v-if="resetInfo?.reset_link" class="reset-link-box">
              <div class="reset-link-title">Reset Link</div>
              <div class="reset-link-value">{{ resetInfo.reset_link }}</div>

              <BaseButton plain @click="copyResetLink">
                <template #iconPre>
                  <el-icon><CopyDocument /></el-icon>
                </template>
                Copy Link
              </BaseButton>
            </div>
          </div>
        </el-card>
      </div>

      <div class="content-grid">
        <el-card shadow="never" class="section-card">
          <div class="card-title">Update Employee</div>

          <el-form label-position="top" class="form-grid">
            <el-form-item label="Full Name" required>
              <el-input v-model="employeeForm.full_name" />
            </el-form-item>

            <el-form-item label="Department">
              <el-input v-model="employeeForm.department" />
            </el-form-item>

            <el-form-item label="Position">
              <el-input v-model="employeeForm.position" />
            </el-form-item>

            <el-form-item label="Manager">
              <el-select
                v-model="employeeForm.manager_user_id"
                clearable
                filterable
                placeholder="Select manager"
                :loading="managerOptionsLoading"
              >
                <el-option
                  v-for="item in managerOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Work Location">
              <el-select
                v-model="employeeForm.work_location_id"
                clearable
                filterable
                placeholder="Select work location"
                :loading="locationOptionsLoading"
              >
                <el-option
                  v-for="item in locationOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Employment Type">
              <el-select v-model="employeeForm.employment_type">
                <el-option label="Permanent" value="permanent" />
                <el-option label="Contract" value="contract" />
              </el-select>
            </el-form-item>

            <el-form-item label="Basic Salary" required>
              <el-input-number
                v-model="employeeForm.basic_salary"
                :min="0"
                :step="10"
                :precision="2"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="Status">
              <el-select v-model="employeeForm.status">
                <el-option label="Active" value="active" />
                <el-option label="Inactive" value="inactive" />
              </el-select>
            </el-form-item>

            <template
              v-if="
                employeeForm.employment_type === 'contract' &&
                employeeForm.contract
              "
            >
              <el-divider />
              <div class="contract-section-title">Contract Details</div>

              <el-form-item label="Start Date" required>
                <el-date-picker
                  v-model="employeeForm.contract.start_date"
                  type="date"
                  placeholder="Select start date"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="End Date" required>
                <el-date-picker
                  v-model="employeeForm.contract.end_date"
                  type="date"
                  placeholder="Select end date"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="Salary Type" required>
                <el-select v-model="employeeForm.contract.salary_type">
                  <el-option label="Monthly" value="monthly" />
                  <el-option label="Daily" value="daily" />
                  <el-option label="Hourly" value="hourly" />
                </el-select>
              </el-form-item>

              <el-form-item label="Rate" required>
                <el-input-number
                  v-model="employeeForm.contract.rate"
                  :min="0"
                  :step="1"
                  :precision="2"
                  controls-position="right"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="employeeForm.contract.pay_on_holiday">
                  Pay on Holiday
                </el-checkbox>
              </el-form-item>

              <el-form-item>
                <el-checkbox v-model="employeeForm.contract.pay_on_weekend">
                  Pay on Weekend
                </el-checkbox>
              </el-form-item>

              <el-form-item label="Leave Policy ID">
                <el-input
                  v-model="employeeForm.contract.leave_policy_id"
                  placeholder="Optional leave policy ID"
                />
              </el-form-item>
            </template>
          </el-form>

          <div class="card-actions">
            <BaseButton
              type="primary"
              :loading="employeeSaving"
              @click="submitEmployeeUpdate"
            >
              Save Employee
            </BaseButton>
          </div>
        </el-card>

        <el-card shadow="never" class="section-card">
          <div class="card-title">Account</div>

          <div
            class="account-badge"
            :class="{ 'account-badge--none': !account }"
          >
            {{ account ? "Account linked" : "No account linked" }}
          </div>

          <el-form label-position="top" class="form-grid">
            <el-form-item label="Email">
              <el-input
                v-model="accountForm.email"
                :disabled="!account"
                placeholder="Email"
              />
            </el-form-item>

            <el-form-item label="Username">
              <el-input
                v-model="accountForm.username"
                :disabled="!account"
                placeholder="Username"
              />
            </el-form-item>

            <el-form-item label="New Password">
              <el-input
                v-model="accountForm.password"
                :disabled="!account"
                type="password"
                show-password
                placeholder="Leave empty to keep current password"
              />
            </el-form-item>
          </el-form>

          <div class="card-actions">
            <BaseButton
              type="primary"
              :disabled="!account"
              :loading="accountSaving"
              @click="submitAccountUpdate"
            >
              Update Account
            </BaseButton>
          </div>

          <el-divider />

          <div class="sub-title">Link Existing Account</div>

          <div class="link-grid">
            <el-select
              v-model="linkForm.user_id"
              filterable
              placeholder="Select account"
              :loading="accountOptionsLoading"
              style="width: 100%"
            >
              <el-option
                v-for="item in accountOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>

            <BaseButton
              type="success"
              :loading="linkSaving"
              @click="submitLinkAccount"
            >
              Link Account
            </BaseButton>
          </div>
        </el-card>

        <el-card shadow="never" class="section-card">
          <div class="card-title">Assign Schedule</div>

          <div class="link-grid">
            <el-select
              v-model="assignForm.schedule_id"
              filterable
              placeholder="Select working schedule"
              :loading="scheduleOptionsLoading"
              style="width: 100%"
            >
              <el-option
                v-for="item in scheduleOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>

            <BaseButton
              type="warning"
              :loading="assignSaving"
              @click="submitAssignSchedule"
            >
              <template #iconPre>
                <el-icon><Refresh /></el-icon>
              </template>
              Assign Schedule
            </BaseButton>
          </div>
        </el-card>
      </div>
    </template>
  </div>
</template>

<style scoped>
.employee-detail-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  max-width: 1460px;
  margin: 0 auto;
  color: var(--text-color, var(--el-text-color-primary));
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.top-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 14px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.profile-card,
.section-card {
  border: 1px solid var(--border-color, var(--el-border-color-light));
  background: var(--color-card, var(--el-bg-color));
  box-shadow: var(--shadow-sm, 0 6px 16px rgba(16, 24, 40, 0.05));
}

.profile-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.profile-info {
  min-width: 0;
}

.profile-avatar {
  background: color-mix(in srgb, var(--el-color-primary) 22%, #ffffff 78%);
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.profile-name {
  font-size: 16px;
  font-weight: 700;
  word-break: break-word;
}

.profile-meta {
  margin-top: 2px;
  font-size: 12px;
  color: var(--muted-color, var(--el-text-color-secondary));
  word-break: break-word;
}

.mini-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.mini-item {
  border: 1px solid var(--border-color, var(--el-border-color-lighter));
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  background: color-mix(in srgb, var(--color-card, #fff) 92%, var(--color-bg, #f7f8fa) 8%);
}

.mini-item span {
  font-size: 11px;
  color: var(--muted-color, var(--el-text-color-secondary));
}

.mini-item strong {
  font-size: 13px;
  color: var(--text-color, var(--el-text-color-primary));
  word-break: break-word;
}

.card-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-color, var(--el-text-color-primary));
}

.sub-title {
  font-size: 13px;
  font-weight: 650;
  margin-bottom: 10px;
  color: var(--text-color, var(--el-text-color-primary));
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.link-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: center;
}

.action-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.account-badge {
  margin-bottom: 10px;
  display: inline-flex;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: var(--color-success-dark-2, var(--el-color-success-dark-2));
  background: color-mix(
    in srgb,
    var(--button-success-bg, var(--el-color-success)) 12%,
    var(--color-card, #fff) 88%
  );
}

.account-badge--none {
  color: var(--color-warning-dark-2, var(--el-color-warning-dark-2));
  background: color-mix(
    in srgb,
    var(--button-warning-bg, var(--el-color-warning)) 14%,
    var(--color-card, #fff) 86%
  );
}

.reset-link-box {
  border: 1px dashed var(--border-color, var(--el-border-color));
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: color-mix(in srgb, var(--color-card, #fff) 94%, var(--color-bg, #f7f8fa) 6%);
}

.reset-link-title {
  font-size: 12px;
  color: var(--muted-color, var(--el-text-color-secondary));
}

.reset-link-value {
  font-size: 12px;
  word-break: break-all;
  color: var(--text-color, var(--el-text-color-primary));
}

.contract-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color, var(--el-text-color-primary));
  margin-bottom: 8px;
}

@media (max-width: 1180px) {
  .top-grid,
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .header-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .link-grid {
    grid-template-columns: 1fr;
  }

  .mini-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    justify-content: stretch;
  }

  .card-actions :deep(button),
  .card-actions :deep(.el-button),
  .card-actions :deep(.base-button) {
    width: 100%;
  }
}
</style>
