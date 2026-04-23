<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  ElCard,
  ElCol,
  ElDescriptions,
  ElDescriptionsItem,
  ElEmpty,
  ElMessage,
  ElProgress,
  ElRow,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  LeaveBalanceDTO,
  LeaveSummaryDTO,
} from "~/api/hr_admin/leave/dto";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const router = useRouter();
const leaveService = hrmsAdminService().leaveRequest;

const loadingBalance = ref(false);
const loadingSummary = ref(false);

const balance = ref<LeaveBalanceDTO | null>(null);
const summary = ref<LeaveSummaryDTO | null>(null);

const loading = computed(() => loadingBalance.value || loadingSummary.value);

const balanceStateType = computed<"success" | "warning" | "danger">(() => {
  const remaining = Number(balance.value?.remaining_days ?? 0);
  if (remaining > 5) return "success";
  if (remaining > 0) return "warning";
  return "danger";
});

const usagePercent = computed(() => {
  const entitlement = Number(balance.value?.annual_entitlement ?? 0);
  const used = Number(balance.value?.used_days ?? 0);
  if (entitlement <= 0) return 0;
  return Math.max(0, Math.min(100, (used / entitlement) * 100));
});

const remainingPercent = computed(() => {
  const entitlement = Number(balance.value?.annual_entitlement ?? 0);
  const remaining = Number(balance.value?.remaining_days ?? 0);
  if (entitlement <= 0) return 0;
  return Math.max(0, Math.min(100, (remaining / entitlement) * 100));
});

const statCards = computed(() => [
  {
    label: "Annual Entitlement",
    value: formatNumber(balance.value?.annual_entitlement),
    hint: "Total leave granted for this cycle",
  },
  {
    label: "Used Days",
    value: formatNumber(balance.value?.used_days),
    hint: "Days already consumed",
  },
  {
    label: "Remaining Days",
    value: formatNumber(balance.value?.remaining_days),
    hint: "Available leave balance",
  },
  {
    label: "Approved Days",
    value: formatNumber(summary.value?.total_approved_days),
    hint: "Total approved leave duration",
  },
]);

const summaryCards = computed(() => [
  {
    label: "Total Requests",
    value: summary.value?.total_requests ?? 0,
  },
  {
    label: "Pending",
    value: summary.value?.pending ?? 0,
  },
  {
    label: "Approved",
    value: summary.value?.approved ?? 0,
  },
  {
    label: "Rejected",
    value: summary.value?.rejected ?? 0,
  },
  {
    label: "Cancelled",
    value: summary.value?.cancelled ?? 0,
  },
]);

function formatNumber(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "0.0";
  return amount.toFixed(1);
}

function formatInteger(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "0";
  return amount.toFixed(0);
}

function progressStatus(
  percentage: number,
): "success" | "warning" | "exception" {
  if (percentage < 70) return "success";
  if (percentage < 90) return "warning";
  return "exception";
}

async function fetchBalance() {
  loadingBalance.value = true;
  try {
    balance.value = await leaveService.getMyBalance();
  } catch {
    ElMessage.error("Failed to load leave balance");
  } finally {
    loadingBalance.value = false;
  }
}

async function fetchSummary() {
  loadingSummary.value = true;
  try {
    summary.value = await leaveService.getMySummary();
  } catch {
    ElMessage.error("Failed to load leave summary");
  } finally {
    loadingSummary.value = false;
  }
}

async function refreshPage() {
  await Promise.all([fetchBalance(), fetchSummary()]);
}

onMounted(() => {
  void refreshPage();
});
</script>

<template>
  <div class="employee-leave-balance-page">
    <OverviewHeader
      title="Leave Balance"
      description="Balance and summary from my-balance and my-summary endpoints"
      :backPath="ROUTES.EMPLOYEE.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="refreshPage">
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loading"
          @click="router.push(ROUTES.EMPLOYEE.LEAVE_REQUEST)"
        >
          Request Leave
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="stats-row">
      <el-col
        v-for="item in statCards"
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

    <el-row :gutter="16" class="main-row">
      <el-col :xs="24" :lg="14">
        <el-card class="panel-card" shadow="never" v-loading="loadingBalance">
          <template #header>
            <div class="panel-header">
              <div>
                <h2 class="panel-title">Balance Breakdown</h2>
                <p class="panel-subtitle">
                  GET /api/hrms/leave-requests/my-balance
                </p>
              </div>
              <ElTag :type="balanceStateType" effect="plain" round>
                {{ Number(balance?.remaining_days ?? 0).toFixed(1) }} day(s)
                left
              </ElTag>
            </div>
          </template>

          <div class="progress-block">
            <div class="progress-block__head">
              <span>Used allocation</span>
              <strong>{{ usagePercent.toFixed(1) }}%</strong>
            </div>
            <ElProgress
              :percentage="Number(usagePercent.toFixed(1))"
              :status="progressStatus(usagePercent)"
              :stroke-width="14"
            />
          </div>

          <div class="progress-block">
            <div class="progress-block__head">
              <span>Remaining allocation</span>
              <strong>{{ remainingPercent.toFixed(1) }}%</strong>
            </div>
            <ElProgress
              :percentage="Number(remainingPercent.toFixed(1))"
              status="success"
              :stroke-width="14"
            />
          </div>

          <ElDescriptions :column="2" border class="mt-4">
            <ElDescriptionsItem label="Annual Entitlement">
              {{ formatNumber(balance?.annual_entitlement) }} day(s)
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Used Days">
              {{ formatNumber(balance?.used_days) }} day(s)
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Remaining Days" :span="2">
              {{ formatNumber(balance?.remaining_days) }} day(s)
            </ElDescriptionsItem>
          </ElDescriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="panel-card" shadow="never" v-loading="loadingSummary">
          <template #header>
            <div class="panel-header">
              <div>
                <h2 class="panel-title">Leave Summary</h2>
                <p class="panel-subtitle">
                  GET /api/hrms/leave-requests/my-summary
                </p>
              </div>
            </div>
          </template>

          <el-row :gutter="12" class="mini-summary-grid">
            <el-col
              v-for="item in summaryCards"
              :key="item.label"
              :xs="12"
              :sm="8"
              :lg="12"
            >
              <div class="mini-summary-card">
                <p class="mini-summary-card__label">{{ item.label }}</p>
                <p class="mini-summary-card__value">
                  {{ formatInteger(item.value) }}
                </p>
              </div>
            </el-col>
          </el-row>

          <ElDescriptions :column="1" border class="mt-4">
            <ElDescriptionsItem label="Total Requests">
              {{ formatInteger(summary?.total_requests) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Approved Days">
              {{ formatNumber(summary?.total_approved_days) }} day(s)
            </ElDescriptionsItem>
          </ElDescriptions>

          <div class="quick-actions">
            <BaseButton
              plain
              @click="router.push(ROUTES.EMPLOYEE.LEAVE_HISTORY)"
            >
              Open History
            </BaseButton>
            <BaseButton
              type="primary"
              @click="router.push(ROUTES.EMPLOYEE.LEAVE_REQUEST)"
            >
              New Request
            </BaseButton>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="panel-header">
          <div>
            <h2 class="panel-title">Guidance</h2>
            <p class="panel-subtitle">
              Use the balance before submitting new leave requests.
            </p>
          </div>
        </div>
      </template>

      <el-empty
        description="Balance and summary are loaded above for quick review"
      />
    </el-card>
  </div>
</template>

<style scoped>
.employee-leave-balance-page {
  padding: 20px;
  max-width: 1520px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 16px;
}

.stat-card {
  border-radius: 16px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  background: linear-gradient(
    180deg,
    var(--color-card) 0%,
    color-mix(in srgb, var(--hover-bg) 28%, var(--color-card) 72%) 100%
  );
  height: 100%;
}

.stat-card__label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted-color);
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
  color: var(--muted-color);
}

.main-row {
  margin-bottom: 16px;
}

.panel-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  box-shadow: 0 14px 36px var(--card-shadow);
  height: 100%;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-dark);
}

.panel-subtitle {
  margin: 4px 0 0;
  color: var(--muted-color);
  font-size: 13px;
}

.progress-block {
  margin-bottom: 14px;
}

.progress-block__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--text-color);
}

.mini-summary-grid {
  margin: 0;
}

.mini-summary-card {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--hover-bg);
  height: 100%;
}

.mini-summary-card__label {
  margin: 0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-color);
}

.mini-summary-card__value {
  margin: 8px 0 0;
  font-size: 20px;
  font-weight: 800;
  color: var(--color-dark);
}

.quick-actions {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
