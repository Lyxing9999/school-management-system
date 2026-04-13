<script setup lang="ts">
import { computed } from "vue";
import { Role } from "~/api/types/enums/role.enum";
import type {
  HrEmploymentType,
  HrEmployeeContractDTO,
  HrSalaryType,
} from "~/api/hr_admin/employees/dto";

type Mode = "employee" | "onboard";

interface EmployeeFormModel {
  employee_code: string;
  full_name: string;
  department: string;
  position: string;
  employment_type: HrEmploymentType;
  basic_salary: number | null;
  status: "active" | "inactive";
  contract: HrEmployeeContractDTO | null;
  email?: string;
  username?: string;
  password?: string;
  role?: Role.EMPLOYEE | Role.MANAGER | Role.PAYROLL_MANAGER;
}

const props = defineProps<{
  modelValue: EmployeeFormModel;
  mode: Mode;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: EmployeeFormModel): void;
}>();

const form = computed({
  get: () => props.modelValue,
  set: (value: EmployeeFormModel) => emit("update:modelValue", value),
});

function defaultContract(): HrEmployeeContractDTO {
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

function update<K extends keyof EmployeeFormModel>(
  key: K,
  value: EmployeeFormModel[K],
) {
  form.value = {
    ...form.value,
    [key]: value,
  };
}

function updateContract<K extends keyof HrEmployeeContractDTO>(
  key: K,
  value: HrEmployeeContractDTO[K],
) {
  form.value = {
    ...form.value,
    contract: {
      ...defaultContract(),
      ...(form.value.contract ?? {}),
      [key]: value,
    },
  };
}

function updateEmploymentType(value: HrEmploymentType) {
  if (value === "contract") {
    form.value = {
      ...form.value,
      employment_type: value,
      contract: form.value.contract ?? defaultContract(),
    };
    return;
  }

  form.value = {
    ...form.value,
    employment_type: value,
    contract: null,
  };
}
</script>

<template>
  <el-form label-position="top" class="dialog-form">
    <div class="form-grid">
      <el-form-item label="Employee Code" required>
        <el-input
          :model-value="form.employee_code"
          placeholder="EMP-001"
          @update:model-value="update('employee_code', $event)"
        />
      </el-form-item>

      <el-form-item label="Full Name" required>
        <el-input
          :model-value="form.full_name"
          placeholder="Employee full name"
          @update:model-value="update('full_name', $event)"
        />
      </el-form-item>

      <el-form-item label="Department">
        <el-input
          :model-value="form.department"
          placeholder="Department"
          @update:model-value="update('department', $event)"
        />
      </el-form-item>

      <el-form-item label="Position">
        <el-input
          :model-value="form.position"
          placeholder="Position"
          @update:model-value="update('position', $event)"
        />
      </el-form-item>

      <el-form-item label="Employment Type">
        <el-select
          :model-value="form.employment_type"
          @update:model-value="updateEmploymentType"
        >
          <el-option label="Permanent" value="permanent" />
          <el-option label="Contract" value="contract" />
        </el-select>
      </el-form-item>

      <el-form-item label="Status">
        <el-select
          :model-value="form.status"
          @update:model-value="update('status', $event)"
        >
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </el-form-item>

      <el-form-item label="Basic Salary" required>
        <el-input-number
          :model-value="form.basic_salary"
          :min="0"
          :step="10"
          :precision="2"
          controls-position="right"
          style="width: 100%"
          @update:model-value="update('basic_salary', $event)"
        />
      </el-form-item>

      <template v-if="mode === 'onboard'">
        <el-form-item label="Email" required>
          <el-input
            :model-value="form.email"
            placeholder="employee@company.com"
            @update:model-value="update('email', $event)"
          />
        </el-form-item>

        <el-form-item label="Username">
          <el-input
            :model-value="form.username"
            placeholder="username (optional)"
            @update:model-value="update('username', $event)"
          />
        </el-form-item>

        <el-form-item label="Password" required>
          <el-input
            :model-value="form.password"
            type="password"
            show-password
            @update:model-value="update('password', $event)"
          />
        </el-form-item>

        <el-form-item label="Role">
          <el-select
            :model-value="form.role"
            @update:model-value="update('role', $event)"
          >
            <el-option label="Employee" :value="Role.EMPLOYEE" />
            <el-option label="Manager" :value="Role.MANAGER" />
            <el-option label="Payroll Manager" :value="Role.PAYROLL_MANAGER" />
          </el-select>
        </el-form-item>
      </template>
    </div>

    <template v-if="form.employment_type === 'contract'">
      <el-divider />

      <div class="contract-title">Contract Details</div>

      <div class="form-grid">
        <el-form-item label="Start Date" required>
          <el-date-picker
            :model-value="form.contract?.start_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="Select start date"
            style="width: 100%"
            @update:model-value="updateContract('start_date', $event)"
          />
        </el-form-item>

        <el-form-item label="End Date" required>
          <el-date-picker
            :model-value="form.contract?.end_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="Select end date"
            style="width: 100%"
            @update:model-value="updateContract('end_date', $event)"
          />
        </el-form-item>

        <el-form-item label="Salary Type" required>
          <el-select
            :model-value="form.contract?.salary_type"
            @update:model-value="updateContract('salary_type', $event)"
          >
            <el-option label="Monthly" value="monthly" />
            <el-option label="Daily" value="daily" />
            <el-option label="Hourly" value="hourly" />
          </el-select>
        </el-form-item>

        <el-form-item label="Rate" required>
          <el-input-number
            :model-value="form.contract?.rate"
            :min="0"
            :step="1"
            :precision="2"
            controls-position="right"
            style="width: 100%"
            @update:model-value="updateContract('rate', $event)"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox
            :model-value="form.contract?.pay_on_holiday"
            @update:model-value="updateContract('pay_on_holiday', $event)"
          >
            Pay on Holiday
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-checkbox
            :model-value="form.contract?.pay_on_weekend"
            @update:model-value="updateContract('pay_on_weekend', $event)"
          >
            Pay on Weekend
          </el-checkbox>
        </el-form-item>

        <el-form-item label="Leave Policy ID">
          <el-input
            :model-value="form.contract?.leave_policy_id ?? ''"
            placeholder="Optional leave policy ID"
            @update:model-value="
              updateContract('leave_policy_id', $event || null)
            "
          />
        </el-form-item>
      </div>
    </template>
  </el-form>
</template>

<style scoped>
.dialog-form {
  margin-top: 6px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 14px;
}

.contract-title {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-color, var(--el-text-color-primary));
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
