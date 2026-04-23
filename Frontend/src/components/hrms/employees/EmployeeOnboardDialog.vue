<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { ElDialog, ElMessage } from "element-plus";
import { Role } from "~/api/types/enums/role.enum";
import type {
  HrCreateEmployeeDTO,
  HrEmployeeAccountListItemDTO,
  HrEmployeeContractDTO,
} from "~/api/hr_admin/employees/dto";
import EmployeeFormFields from "~/components/hrms/employees/EmployeeFormFields.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { useHrEmployeeStore } from "~/stores/hrEmployeeStore";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

type HrOnboardRole = Role.EMPLOYEE | Role.MANAGER | Role.PAYROLL_MANAGER;

type EmployeeFormModel = {
  employee_code: string;
  full_name: string;
  department: string;
  position: string;
  manager_user_id: string | null;
  employment_type: "permanent" | "contract";
  basic_salary: number | null;
  status: "active" | "inactive";
  contract: HrEmployeeContractDTO | null;
  email: string;
  username: string;
  password: string;
  role?: HrOnboardRole;
};

const props = defineProps<{
  visible: boolean;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:visible", value: boolean): void;
  (
    e: "submitted",
    payload: {
      employee: HrCreateEmployeeDTO;
      account: {
        email: string;
        password: string;
        username?: string;
        role?: HrOnboardRole;
      };
    },
  ): void;
}>();

function createDefaultContract(): HrEmployeeContractDTO {
  return {
    start_date: "",
    end_date: "",
    salary_type: "monthly",
    rate: 0,
    pay_on_holiday: false,
    pay_on_weekend: false,
    leave_policy_id: null,
  };
}

function createDefaultForm(): EmployeeFormModel {
  return {
    employee_code: "",
    full_name: "",
    department: "",
    position: "",
    manager_user_id: null,
    employment_type: "permanent",
    basic_salary: null,
    status: "active",
    contract: null,
    email: "",
    username: "",
    password: "",
    role: undefined,
  };
}

const form = ref<EmployeeFormModel>(createDefaultForm());
const employeeStore = useHrEmployeeStore();
const managerOptionsLoading = ref(false);
const managerOptions = ref<Array<{ value: string; label: string }>>([]);

watch(
  () => form.value.employment_type,
  (type) => {
    if (type === "contract" && !form.value.contract) {
      form.value = {
        ...form.value,
        contract: createDefaultContract(),
      };
    }

    if (type === "permanent" && form.value.contract) {
      form.value = {
        ...form.value,
        contract: null,
      };
    }
  },
);

const canSubmit = computed(() => {
  const current = form.value;

  const baseValid =
    current.employee_code.trim().length > 0 &&
    current.full_name.trim().length > 0 &&
    Number(current.basic_salary ?? -1) >= 0 &&
    current.email.trim().length > 0 &&
    current.password.length >= 6;

  if (!baseValid) return false;

  if (current.employment_type === "contract") {
    return Boolean(
      current.contract &&
        current.contract.start_date &&
        current.contract.end_date &&
        current.contract.salary_type &&
        Number(current.contract.rate ?? -1) >= 0,
    );
  }

  return true;
});

function resetForm() {
  form.value = createDefaultForm();
}

function closeDialog() {
  emit("update:visible", false);
}

function handleClosed() {
  resetForm();
}

function normalizeRole(raw?: string | null): string {
  return String(raw ?? "")
    .trim()
    .toLowerCase();
}

function buildAccountOptionLabel(
  item: HrEmployeeAccountListItemDTO,
  fallbackLabel: string,
): string {
  const primary = displayRelation(
    item.account_name ?? item.username ?? item.email,
    item.user_id ?? item.id,
    fallbackLabel,
  );
  const secondary = String(item.account_email ?? item.email ?? "").trim();
  if (!secondary || secondary === primary) return primary;
  return `${primary} • ${secondary}`;
}

async function loadManagerOptions() {
  managerOptionsLoading.value = true;
  try {
    const response = await employeeStore.getEmployeeAccounts({
      page: 1,
      limit: 500,
      status: "active",
    });

    managerOptions.value = (response.items ?? [])
      .filter((item) => normalizeRole(item.role) === "manager")
      .map((item) => ({
        value: String(item.user_id ?? item.id),
        label: buildAccountOptionLabel(item, "Manager"),
      }));
  } catch {
    managerOptions.value = [];
  } finally {
    managerOptionsLoading.value = false;
  }
}

watch(
  () => props.visible,
  (visible) => {
    if (visible && !managerOptions.value.length) {
      void loadManagerOptions();
    }
  },
  { immediate: true },
);

function submit() {
  const current = form.value;

  if (!current.employee_code.trim()) {
    ElMessage.error("Employee code is required");
    return;
  }

  if (!current.full_name.trim()) {
    ElMessage.error("Full name is required");
    return;
  }

  if (current.basic_salary == null || Number(current.basic_salary) < 0) {
    ElMessage.error("Basic salary must be 0 or greater");
    return;
  }

  if (!current.email.trim()) {
    ElMessage.error("Email is required");
    return;
  }

  if (current.password.length < 6) {
    ElMessage.error("Password must be at least 6 characters");
    return;
  }

  if (current.employment_type === "contract") {
    if (!current.contract?.start_date) {
      ElMessage.error("Contract start date is required");
      return;
    }
    if (!current.contract?.end_date) {
      ElMessage.error("Contract end date is required");
      return;
    }
    if (!current.contract?.salary_type) {
      ElMessage.error("Contract salary type is required");
      return;
    }
    if (current.contract.rate == null || Number(current.contract.rate) < 0) {
      ElMessage.error("Contract rate must be 0 or greater");
      return;
    }
  }

  const employee: HrCreateEmployeeDTO = {
    employee_code: current.employee_code.trim(),
    full_name: current.full_name.trim(),
    department: current.department.trim() || null,
    position: current.position.trim() || null,
    manager_user_id: current.manager_user_id || null,
    employment_type: current.employment_type,
    basic_salary: Number(current.basic_salary),
    status: current.status,
    contract:
      current.employment_type === "contract" && current.contract
        ? {
            start_date: current.contract.start_date,
            end_date: current.contract.end_date,
            salary_type: current.contract.salary_type,
            rate: Number(current.contract.rate),
            pay_on_holiday: Boolean(current.contract.pay_on_holiday),
            pay_on_weekend: Boolean(current.contract.pay_on_weekend),
            leave_policy_id: current.contract.leave_policy_id ?? null,
          }
        : null,
  };

  const account = {
    email: current.email.trim(),
    password: current.password,
    username: current.username.trim() || undefined,
    role: current.role,
  };

  emit("submitted", { employee, account });
}
</script>

<template>
  <ElDialog
    :model-value="visible"
    title="Onboard Employee"
    width="900px"
    destroy-on-close
    @update:model-value="emit('update:visible', $event)"
    @closed="handleClosed"
  >
    <EmployeeFormFields
      v-model="form"
      mode="onboard"
      :manager-options="managerOptions"
      :manager-options-loading="managerOptionsLoading"
    />

    <template #footer>
      <div class="dialog-actions">
        <BaseButton plain :disabled="loading" @click="closeDialog">
          Cancel
        </BaseButton>
        <BaseButton
          type="primary"
          :loading="loading"
          :disabled="!canSubmit"
          @click="submit"
        >
          Create Employee + Account
        </BaseButton>
      </div>
    </template>
  </ElDialog>
</template>

<style scoped>
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
