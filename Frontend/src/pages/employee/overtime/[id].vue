<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ElButton,
  ElCard,
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElEmpty,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  OvertimeCancelDTO,
  OvertimeRequestDTO,
} from "~/api/hr_admin/overtime/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const route = useRoute();
const router = useRouter();
const overtimeService = hrmsAdminService().overtimeRequest;

const overtimeId = computed(() => String(route.params.id || ""));

const loading = ref(false);
const actionLoading = ref(false);
const overtime = ref<OvertimeRequestDTO | null>(null);

const cancelDialogVisible = ref(false);
const cancelForm = reactive<OvertimeCancelDTO>({
  reason: "",
});

const canCancel = computed(
  () => String(overtime.value?.status || "").toLowerCase() === "pending",
);

function formatDate(value?: string | null): string {
  if (!value) return "-";

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-");
    return new Date(
      Number(year),
      Number(month) - 1,
      Number(day),
    ).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  }

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

function formatMoney(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "-";

  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatHours(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "0.00";
  return amount.toFixed(2);
}

function dayTypeLabel(dayType?: string | null): string {
  const map: Record<string, string> = {
    working_day: "Working Day",
    weekend: "Weekend",
    public_holiday: "Public Holiday",
  };

  return map[String(dayType || "").toLowerCase()] || "Unknown";
}

function statusTagType(
  status?: string | null,
): "warning" | "success" | "danger" | "info" {
  const map: Record<string, "warning" | "success" | "danger" | "info"> = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
    cancelled: "info",
  };

  return map[String(status || "").toLowerCase()] || "info";
}

function statusClass(status?: string | null): string {
  const map: Record<string, string> = {
    pending: "status-pill status-pill--pending",
    approved: "status-pill status-pill--approved",
    rejected: "status-pill status-pill--rejected",
    cancelled: "status-pill status-pill--cancelled",
  };

  return map[String(status || "").toLowerCase()] || "status-pill";
}

async function fetchDetail() {
  if (!overtimeId.value) return;

  loading.value = true;
  try {
    overtime.value = await overtimeService.getRequest(overtimeId.value);
  } catch {
    ElMessage.error("Failed to load overtime request detail");
  } finally {
    loading.value = false;
  }
}

function openCancelDialog() {
  cancelForm.reason = "";
  cancelDialogVisible.value = true;
}

function closeCancelDialog() {
  cancelDialogVisible.value = false;
  cancelForm.reason = "";
}

async function submitCancel() {
  if (!overtime.value || !canCancel.value) return;

  try {
    await ElMessageBox.confirm(
      "Cancel this pending overtime request?",
      "Confirm Cancel",
      {
        confirmButtonText: "Cancel Request",
        cancelButtonText: "Keep Request",
        type: "warning",
      },
    );
  } catch {
    return;
  }

  actionLoading.value = true;
  try {
    await overtimeService.cancelRequest(overtime.value.id, {
      reason: String(cancelForm.reason || "").trim() || null,
    });

    ElMessage.success("Overtime request cancelled");
    closeCancelDialog();
    await fetchDetail();
  } catch {
    ElMessage.error("Failed to cancel overtime request");
  } finally {
    actionLoading.value = false;
  }
}

onMounted(() => {
  void fetchDetail();
});
</script>

<template>
  <div class="employee-overtime-detail-page">
    <OverviewHeader
      :title="`Overtime Detail (${overtimeId || '-'})`"
      description="Detail of one overtime request from /api/hrms/overtime-requests/:id"
      :backPath="ROUTES.EMPLOYEE.OVERTIME_HISTORY"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="fetchDetail"
          >Refresh</BaseButton
        >

        <BaseButton
          plain
          :disabled="loading || actionLoading"
          @click="router.push(ROUTES.EMPLOYEE.OVERTIME_HISTORY)"
        >
          Back
        </BaseButton>
      </template>
    </OverviewHeader>

    <ElCard class="detail-card" shadow="never" v-loading="loading">
      <template v-if="overtime">
        <div class="detail-head">
          <div>
            <h3 class="detail-title">Request Information</h3>
            <p class="detail-subtitle">Request ID {{ overtime.id }}</p>
          </div>

          <ElTag
            :type="statusTagType(overtime.status)"
            effect="plain"
            round
            size="small"
            :class="statusClass(overtime.status)"
          >
            {{
              String(overtime.status || "-")
                .charAt(0)
                .toUpperCase() + String(overtime.status || "-").slice(1)
            }}
          </ElTag>
        </div>

        <ElDescriptions :column="2" border class="mt-4">
          <ElDescriptionsItem label="Request Date">
            {{ formatDate(overtime.request_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Submitted At">
            {{ formatDateTime(overtime.submitted_at) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Start Time">
            {{ formatDateTime(overtime.start_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="End Time">
            {{ formatDateTime(overtime.end_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Schedule End Time">
            {{ formatDateTime(overtime.schedule_end_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Day Type">
            {{ dayTypeLabel(overtime.day_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Approved Hours">
            {{ formatHours(overtime.approved_hours) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Calculated Payment">
            {{ formatMoney(overtime.calculated_payment) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Basic Salary">
            {{ formatMoney(overtime.basic_salary) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager">
            {{
              displayRelation(
                overtime.manager_name,
                overtime.manager_user_id || overtime.manager_id,
              )
            }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Reason" :span="2">
            {{ overtime.reason }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager Comment" :span="2">
            {{ overtime.manager_comment || "-" }}
          </ElDescriptionsItem>
        </ElDescriptions>

        <div v-if="canCancel" class="action-row">
          <ElButton
            type="danger"
            :loading="actionLoading"
            @click="openCancelDialog"
          >
            Cancel Request
          </ElButton>
        </div>
      </template>

      <ElEmpty v-else description="No overtime request found for this ID" />
    </ElCard>

    <ElDialog
      v-model="cancelDialogVisible"
      title="Cancel Overtime Request"
      width="560px"
      @close="closeCancelDialog"
    >
      <ElForm label-width="100px">
        <ElFormItem label="Reason">
          <ElInput
            v-model="cancelForm.reason"
            type="textarea"
            :rows="4"
            placeholder="Optional cancellation reason"
          />
        </ElFormItem>
      </ElForm>

      <template #footer>
        <ElButton @click="closeCancelDialog">Close</ElButton>
        <ElButton type="danger" :loading="actionLoading" @click="submitCancel">
          Confirm Cancel
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.employee-overtime-detail-page {
  padding: 20px;
  max-width: 1320px;
  margin: 0 auto;
}

.detail-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, white 18%);
  box-shadow: 0 14px 36px rgba(16, 24, 40, 0.06);
}

.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-dark);
}

.detail-subtitle {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.action-row {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-pill {
  font-weight: 650;
  letter-spacing: 0.01em;
}

.status-pill--pending {
  border-color: #e6a23c;
  color: #b88230;
  background: #fff8eb;
}

.status-pill--approved {
  border-color: #67c23a;
  color: #3b8f1d;
  background: #f1faec;
}

.status-pill--rejected {
  border-color: #f56c6c;
  color: #c74141;
  background: #fff2f2;
}

.status-pill--cancelled {
  border-color: #909399;
  color: #61656d;
  background: #f5f6f7;
}

@media (max-width: 768px) {
  .detail-head,
  .action-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
