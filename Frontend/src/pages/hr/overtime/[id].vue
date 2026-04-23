<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ElButton,
  ElCard,
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElTag,
  type FormInstance,
  type FormRules,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  OvertimeApproveDTO,
  OvertimeRejectDTO,
  OvertimeRequestDTO,
} from "~/api/hr_admin/overtime/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { useAuthStore } from "~/stores/authStore";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const overtimeService = hrmsAdminService().overtimeRequest;

const overtimeId = computed(() => String(route.params.id || ""));

const loading = ref(false);
const actionLoading = ref(false);
const overtime = ref<OvertimeRequestDTO | null>(null);

const approveDialogVisible = ref(false);
const rejectDialogVisible = ref(false);
const approveFormRef = ref<FormInstance>();
const rejectFormRef = ref<FormInstance>();

const approveForm = reactive<OvertimeApproveDTO>({
  approved_hours: 0,
  comment: null,
});

const rejectForm = reactive<OvertimeRejectDTO>({
  comment: "",
});

const approveRules: FormRules = {
  approved_hours: [
    {
      required: true,
      message: "Approved hours is required",
      trigger: "change",
    },
    {
      validator: (_rule, value: number, callback) => {
        if (!Number.isFinite(Number(value)) || Number(value) <= 0) {
          callback(new Error("Approved hours must be greater than 0"));
          return;
        }
        callback();
      },
      trigger: "change",
    },
  ],
};

const rejectRules: FormRules = {
  comment: [
    {
      required: true,
      message: "Rejection comment is required",
      trigger: "blur",
    },
  ],
};

const canReview = computed(() => {
  const role = authStore.user?.role;
  return role === "hr_admin" || role === "manager";
});

const isPending = computed(() => overtime.value?.status === "pending");

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

function estimateHours(row: OvertimeRequestDTO): number {
  if (typeof row.approved_hours === "number" && row.approved_hours > 0) {
    return Number(row.approved_hours.toFixed(2));
  }

  const start = new Date(row.start_time);
  const end = new Date(row.end_time);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 1;

  const hours = (end.getTime() - start.getTime()) / 3_600_000;
  return hours > 0 ? Number(hours.toFixed(2)) : 1;
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

function openApproveDialog() {
  if (!overtime.value) return;
  approveForm.approved_hours = estimateHours(overtime.value);
  approveForm.comment = null;
  approveDialogVisible.value = true;
}

function openRejectDialog() {
  rejectForm.comment = "";
  rejectDialogVisible.value = true;
}

async function submitApprove() {
  if (!overtime.value) return;

  await approveFormRef.value?.validate();

  actionLoading.value = true;
  try {
    await overtimeService.approveRequest(overtime.value.id, {
      approved_hours: Number(approveForm.approved_hours),
      comment: String(approveForm.comment || "").trim() || null,
    });

    ElMessage.success("Overtime request approved");
    approveDialogVisible.value = false;
    await fetchDetail();
  } catch {
    ElMessage.error("Failed to approve overtime request");
  } finally {
    actionLoading.value = false;
  }
}

async function submitReject() {
  if (!overtime.value) return;

  await rejectFormRef.value?.validate();

  actionLoading.value = true;
  try {
    await overtimeService.rejectRequest(overtime.value.id, {
      comment: String(rejectForm.comment || "").trim(),
    });

    ElMessage.success("Overtime request rejected");
    rejectDialogVisible.value = false;
    await fetchDetail();
  } catch {
    ElMessage.error("Failed to reject overtime request");
  } finally {
    actionLoading.value = false;
  }
}

await fetchDetail();
</script>

<template>
  <OverviewHeader
    :title="`Overtime Detail (${overtimeId || '-'})`"
    :description="'Review a single overtime request and optionally approve or reject it'"
    :backPath="ROUTES.HR_ADMIN.OVERTIME"
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
        @click="router.push(ROUTES.HR_ADMIN.OVERTIME)"
      >
        Back
      </BaseButton>
    </template>
  </OverviewHeader>

  <ElCard v-loading="loading">
    <template v-if="overtime">
      <div class="detail-head">
        <h3 class="detail-title">Request Information</h3>
        <ElTag
          :type="statusTagType(overtime.status)"
          effect="plain"
          round
          size="small"
          :class="statusClass(overtime.status)"
        >
          {{
            overtime.status.charAt(0).toUpperCase() + overtime.status.slice(1)
          }}
        </ElTag>
      </div>

      <ElDescriptions :column="2" border class="mt-3">
        <ElDescriptionsItem label="ID">{{ overtime.id }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Employee">{{
          displayRelation(overtime.employee_name, overtime.employee_id)
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Request Date">{{
          overtime.request_date
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Submitted At">{{
          formatDateTime(overtime.submitted_at)
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Start Time">{{
          formatDateTime(overtime.start_time)
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="End Time">{{
          formatDateTime(overtime.end_time)
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Approved Hours">{{
          overtime.approved_hours || 0
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Calculated Payment">{{
          overtime.calculated_payment || 0
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Day Type">{{
          overtime.day_type
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Basic Salary">{{
          overtime.basic_salary || 0
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Reason" :span="2">{{
          overtime.reason
        }}</ElDescriptionsItem>
        <ElDescriptionsItem label="Manager Comment" :span="2">{{
          overtime.manager_comment || "-"
        }}</ElDescriptionsItem>
      </ElDescriptions>

      <div v-if="canReview && isPending" class="action-row">
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
      <div class="empty-box">No overtime request found for this ID.</div>
    </template>
  </ElCard>

  <ElDialog
    v-model="approveDialogVisible"
    title="Approve Overtime Request"
    width="520px"
  >
    <ElForm
      ref="approveFormRef"
      :model="approveForm"
      :rules="approveRules"
      label-width="120px"
    >
      <ElFormItem label="Approved Hours" prop="approved_hours">
        <ElInputNumber
          v-model="approveForm.approved_hours"
          :min="0.25"
          :max="24"
          :step="0.25"
          :precision="2"
          class="w-full"
        />
      </ElFormItem>
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
      <ElButton @click="approveDialogVisible = false">Cancel</ElButton>
      <ElButton type="success" :loading="actionLoading" @click="submitApprove">
        Approve
      </ElButton>
    </template>
  </ElDialog>

  <ElDialog
    v-model="rejectDialogVisible"
    title="Reject Overtime Request"
    width="520px"
  >
    <ElForm
      ref="rejectFormRef"
      :model="rejectForm"
      :rules="rejectRules"
      label-width="120px"
    >
      <ElFormItem label="Comment" prop="comment">
        <ElInput
          v-model="rejectForm.comment"
          type="textarea"
          :rows="4"
          placeholder="Required rejection comment"
        />
      </ElFormItem>
    </ElForm>

    <template #footer>
      <ElButton @click="rejectDialogVisible = false">Cancel</ElButton>
      <ElButton type="danger" :loading="actionLoading" @click="submitReject">
        Reject
      </ElButton>
    </template>
  </ElDialog>
</template>

<style scoped>
.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-title {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.action-row {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-box {
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
}

.status-pill {
  font-weight: 600;
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
</style>
