<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  ElButton,
  ElCard,
  ElDescriptions,
  ElDescriptionsItem,
  ElEmpty,
  ElMessage,
  ElRow,
  ElCol,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  HrEmployeeDTO,
  HrSalaryType,
  HrEmploymentType,
} from "~/api/hr_admin/employees/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const employeeService = hrmsAdminService().employee;

const loading = ref(false);
const employee = ref<HrEmployeeDTO | null>(null);

const statusType = computed<"success" | "danger" | "warning" | "info">(() => {
  const key = String(employee.value?.status || "").toLowerCase();
  if (key === "active") return "success";
  if (key === "inactive") return "danger";
  return "info";
});

const profileStats = computed(() => {
  const e = employee.value;
  const contract = e?.contract;

  return [
    {
      label: "Employee Code",
      value: e?.employee_code || "-",
      hint: "Unique profile identifier",
    },
    {
      label: "Status",
      value: String(e?.status || "-").toUpperCase(),
      hint: "Current employment status",
    },
    {
      label: "Employment Type",
      value: employmentTypeLabel(e?.employment_type),
      hint: "Permanent or contract",
    },
    {
      label: "Salary Type",
      value: salaryTypeLabel(contract?.salary_type),
      hint: "Monthly, daily, or hourly",
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

function salaryTypeLabel(value?: HrSalaryType | null): string {
  const map: Record<string, string> = {
    monthly: "Monthly",
    daily: "Daily",
    hourly: "Hourly",
  };

  return map[String(value || "").toLowerCase()] || "-";
}

function employmentTypeLabel(value?: HrEmploymentType | null): string {
  const map: Record<string, string> = {
    permanent: "Permanent",
    contract: "Contract",
  };

  return map[String(value || "").toLowerCase()] || "-";
}

async function fetchProfile() {
  loading.value = true;
  try {
    employee.value = await employeeService.getMyEmployee();
  } catch {
    ElMessage.error("Failed to load employee profile");
  } finally {
    loading.value = false;
  }
}

async function refreshProfile() {
  await fetchProfile();
  ElMessage.success("Profile refreshed");
}

onMounted(() => {
  void fetchProfile();
});
</script>

<template>
  <div class="employee-profile-page">
    <OverviewHeader
      title="My Profile"
      description="Personal employee profile from /api/hrms/employees/me"
      :backPath="ROUTES.EMPLOYEE.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="refreshProfile">
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="stats-row">
      <el-col
        v-for="item in profileStats"
        :key="item.label"
        :xs="24"
        :sm="12"
        :lg="6"
      >
        <el-card class="stat-card" shadow="never" v-loading="loading">
          <p class="stat-card__label">{{ item.label }}</p>
          <p class="stat-card__value">{{ item.value }}</p>
          <p class="stat-card__hint">{{ item.hint }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="profile-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="profile-card__header">
          <div>
            <h2 class="profile-card__title">Profile Information</h2>
            <p class="profile-card__subtitle">
              Employee identity and work details
            </p>
          </div>
          <ElTag :type="statusType" effect="plain" round>
            {{ String(employee?.status || "-").toUpperCase() }}
          </ElTag>
        </div>
      </template>

      <template v-if="employee">
        <ElDescriptions :column="2" border>
          <ElDescriptionsItem label="Full Name">
            {{ employee.full_name || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Employee Code">
            {{ employee.employee_code || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Department">
            {{ employee.department || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Position">
            {{ employee.position || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Employment Type">
            {{ employmentTypeLabel(employee.employment_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Basic Salary">
            {{ formatMoney(employee.basic_salary) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Status">
            {{ String(employee.status || "-").toUpperCase() }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Account">
            {{
              displayRelation(
                employee.account_name || employee.account_email,
                employee.user_id,
              )
            }}
          </ElDescriptionsItem>
        </ElDescriptions>

        <div class="section-separator"></div>

        <div class="section-title">Contract</div>
        <ElDescriptions :column="2" border>
          <ElDescriptionsItem label="Start Date">
            {{ formatDate(employee.contract?.start_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="End Date">
            {{ formatDate(employee.contract?.end_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Salary Type">
            {{ salaryTypeLabel(employee.contract?.salary_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Rate">
            {{ formatMoney(employee.contract?.rate) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Pay On Holiday">
            {{ employee.contract?.pay_on_holiday ? "Yes" : "No" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Pay On Weekend">
            {{ employee.contract?.pay_on_weekend ? "Yes" : "No" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Leave Policy ID" :span="2">
            {{ employee.contract?.leave_policy_id || "-" }}
          </ElDescriptionsItem>
        </ElDescriptions>

        <div class="section-separator"></div>

        <div class="section-title">Lifecycle</div>
        <ElDescriptions :column="2" border>
          <ElDescriptionsItem label="Created At">
            {{ formatDateTime(employee.lifecycle?.created_at) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Updated At">
            {{ formatDateTime(employee.lifecycle?.updated_at) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Deleted At" :span="2">
            {{ formatDateTime(employee.lifecycle?.deleted_at) }}
          </ElDescriptionsItem>
        </ElDescriptions>
      </template>

      <ElEmpty v-else description="No employee profile data found" />

      <div class="actions-row">
        <ElButton :loading="loading" @click="fetchProfile">Reload</ElButton>
        <ElButton
          type="primary"
          plain
          @click="$router.push(ROUTES.EMPLOYEE.DASHBOARD)"
        >
          Go Dashboard
        </ElButton>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.employee-profile-page {
  padding: 20px;
  max-width: 1320px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  border-radius: 16px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, white 18%);
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  height: 100%;
}

.stat-card__label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #7a7f89;
}

.stat-card__value {
  margin: 8px 0 4px;
  font-size: 24px;
  line-height: 1.1;
  font-weight: 800;
  color: var(--color-dark);
}

.stat-card__hint {
  margin: 0;
  font-size: 12px;
  color: #8a8f98;
}

.profile-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, white 18%);
  box-shadow: 0 14px 36px rgba(16, 24, 40, 0.06);
}

.profile-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.profile-card__title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-dark);
}

.profile-card__subtitle {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.section-separator {
  height: 1px;
  margin: 16px 0;
  background: #e5e7eb;
}

.section-title {
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #6b7280;
}

.actions-row {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .profile-card__header,
  .actions-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
