<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
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
  ElTag,
  type FormInstance,
  type FormRules,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  LeaveApproveDTO,
  LeaveRejectDTO,
  LeaveRequestDTO,
} from "~/api/hr_admin/leave/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const route = useRoute();
const router = useRouter();
const leaveService = hrmsAdminService().leaveRequest;

const leaveId = computed(() => String(route.params.id || ""));

const loading = ref(false);
const actionLoading = ref(false);
const leaveRequest = ref<LeaveRequestDTO | null>(null);

const approveDialogVisible = ref(false);
const rejectDialogVisible = ref(false);
const approveFormRef = ref<FormInstance>();
const rejectFormRef = ref<FormInstance>();

const approveForm = reactive<LeaveApproveDTO>({
  comment: null,
});

const rejectForm = reactive<LeaveRejectDTO>({
  comment: null,
});

const approveRules: FormRules = {
  comment: [
    {
      validator: (_rule, value: string | null | undefined, callback) => {
        if (value == null) {
          callback();
          return;
        }

        callback();
      },
      trigger: "blur",
    },
  ],
};

const rejectRules: FormRules = {
  comment: [
    {
      validator: (_rule, value: string | null | undefined, callback) => {
        if (value == null) {
          callback();
          return;
        }

        callback();
      },
      trigger: "blur",
    },
  ],
};

const isPending = computed(() => leaveRequest.value?.status === "pending");

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

function statusTagType(
  status?: string,
): "warning" | "success" | "danger" | "info" {
  const map: Record<string, "warning" | "success" | "danger" | "info"> = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
    cancelled: "info",
  };

  return map[String(status || "").toLowerCase()] || "info";
}

function statusClass(status?: string): string {
  const map: Record<string, string> = {
    pending: "status-pill status-pill--pending",
    approved: "status-pill status-pill--approved",
    rejected: "status-pill status-pill--rejected",
    cancelled: "status-pill status-pill--cancelled",
  };

  return map[String(status || "").toLowerCase()] || "status-pill";
}

function leaveTypeLabel(value?: string | null): string {
  if (!value) return "-";

  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatMoney(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "-";

  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

async function fetchDetail() {
  if (!leaveId.value) return;

  loading.value = true;
  try {
    leaveRequest.value = await leaveService.getRequest(leaveId.value);
  } catch {
    ElMessage.error("Failed to load leave request detail");
  } finally {
    loading.value = false;
  }
}

watch(
  () => leaveId.value,
  async (nextId, prevId) => {
    if (!nextId || nextId === prevId) return;

    // Prevent stale actions from the previous request when route id changes.
    approveDialogVisible.value = false;
    rejectDialogVisible.value = false;
    actionLoading.value = false;
    leaveRequest.value = null;

    await fetchDetail();
  },
);

function openApproveDialog() {
  if (!leaveRequest.value) return;

  approveForm.comment = null;
  approveDialogVisible.value = true;
}

function openRejectDialog() {
  if (!leaveRequest.value) return;

  rejectForm.comment = null;
  rejectDialogVisible.value = true;
}

function closeApproveDialog() {
  approveDialogVisible.value = false;
  approveForm.comment = null;
}

function closeRejectDialog() {
  rejectDialogVisible.value = false;
  rejectForm.comment = null;
}

async function submitApprove() {
  if (!leaveRequest.value) return;

  await approveFormRef.value?.validate();

  actionLoading.value = true;
  try {
    await leaveService.approveRequest(leaveRequest.value.id, {
      comment: String(approveForm.comment || "").trim() || null,
    });

    ElMessage.success("Leave request approved");
    approveDialogVisible.value = false;
    await fetchDetail();
  } catch {
    ElMessage.error("Failed to approve leave request");
  } finally {
    actionLoading.value = false;
  }
}

async function submitReject() {
  if (!leaveRequest.value) return;

  await rejectFormRef.value?.validate();

  actionLoading.value = true;
  try {
    await leaveService.rejectRequest(leaveRequest.value.id, {
      comment: String(rejectForm.comment || "").trim() || null,
    });

    ElMessage.success("Leave request rejected");
    rejectDialogVisible.value = false;
    await fetchDetail();
  } catch {
    ElMessage.error("Failed to reject leave request");
  } finally {
    actionLoading.value = false;
  }
}

onMounted(() => {
  fetchDetail();
});
</script>

<template>
  <div class="leave-detail-page">
    <OverviewHeader
      :title="`Leave Detail (${leaveId || '-'})`"
      :description="'Review a single leave request and approve or reject it'"
      :backPath="ROUTES.HR_ADMIN.LEAVES"
    >
      <template #actions>
        <BaseButton
          plain
          :loading="loading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="fetchDetail"
        >
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loading || actionLoading"
          @click="router.push(ROUTES.HR_ADMIN.LEAVES)"
        >
          Back
        </BaseButton>
      </template>
    </OverviewHeader>

    <ElCard v-loading="loading" class="detail-card">
      <template v-if="leaveRequest">
        <div class="detail-head">
          <div>
            <h3 class="detail-title">Request Information</h3>
            <p class="detail-subtitle">Leave request {{ leaveRequest.id }}</p>
          </div>

          <ElTag
            :type="statusTagType(leaveRequest.status)"
            effect="plain"
            round
            size="small"
            :class="statusClass(leaveRequest.status)"
          >
            {{
              leaveRequest.status.charAt(0).toUpperCase() +
              leaveRequest.status.slice(1)
            }}
          </ElTag>
        </div>

        <ElDescriptions :column="2" border class="mt-3">
          <ElDescriptionsItem label="ID">{{
            leaveRequest.id
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Employee">{{
            displayRelation(leaveRequest.employee_name, leaveRequest.employee_id)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Leave Type">{{
            leaveTypeLabel(leaveRequest.leave_type)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Paid Leave">{{
            leaveRequest.is_paid ? "Yes" : "No"
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Start Date">{{
            formatDate(leaveRequest.start_date)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="End Date">{{
            formatDate(leaveRequest.end_date)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Total Days">{{
            Number(leaveRequest.total_days || 0).toFixed(1)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Manager">{{
            displayRelation(leaveRequest.manager_name, leaveRequest.manager_user_id)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Contract Start">{{
            formatDate(leaveRequest.contract_start)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Contract End">{{
            formatDate(leaveRequest.contract_end)
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Reason" :span="2">{{
            leaveRequest.reason
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Manager Comment" :span="2">{{
            leaveRequest.manager_comment || "-"
          }}</ElDescriptionsItem>
          <ElDescriptionsItem label="Lifecycle" :span="2">
            <pre class="lifecycle-json">{{
              JSON.stringify(leaveRequest.lifecycle, null, 2)
            }}</pre>
          </ElDescriptionsItem>
        </ElDescriptions>

        <div v-if="isPending" class="action-row">
          <ElButton
            type="success"
            :loading="actionLoading"
            @click="openApproveDialog"
          >
            Approve
          </ElButton>
          <ElButton
            type="danger"
            :loading="actionLoading"
            @click="openRejectDialog"
          >
            Reject
          </ElButton>
        </div>
      </template>

      <template v-else>
        <ElEmpty description="No leave request found for this ID" />
      </template>
    </ElCard>

    <ElDialog
      v-model="approveDialogVisible"
      title="Approve Leave Request"
      width="520px"
    >
      <ElForm
        ref="approveFormRef"
        :model="approveForm"
        :rules="approveRules"
        label-width="120px"
      >
        <ElFormItem label="Comment">
          <ElInput
            v-model="approveForm.comment"
            type="textarea"
            :rows="3"
            placeholder="Optional approval comment"
          />
        </ElFormItem>
      </ElForm>

      <template #footer>
        <ElButton @click="closeApproveDialog">Cancel</ElButton>
        <ElButton
          type="success"
          :loading="actionLoading"
          @click="submitApprove"
        >
          Approve
        </ElButton>
      </template>
    </ElDialog>

    <ElDialog
      v-model="rejectDialogVisible"
      title="Reject Leave Request"
      width="520px"
    >
      <ElForm
        ref="rejectFormRef"
        :model="rejectForm"
        :rules="rejectRules"
        label-width="120px"
      >
        <ElFormItem label="Comment">
          <ElInput
            v-model="rejectForm.comment"
            type="textarea"
            :rows="4"
            placeholder="Optional rejection comment"
          />
        </ElFormItem>
      </ElForm>

      <template #footer>
        <ElButton @click="closeRejectDialog">Cancel</ElButton>
        <ElButton type="danger" :loading="actionLoading" @click="submitReject">
          Reject
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.leave-detail-page {
  padding: 20px;
  max-width: 1280px;
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

.lifecycle-json {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  color: #4b5563;
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
  .detail-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
