<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import {
  ElButton,
  ElCard,
  ElCol,
  ElDatePicker,
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElEmpty,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElMessageBox,
  ElPagination,
  ElRow,
  ElTable,
  ElTableColumn,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  OvertimeApproveDTO,
  OvertimeRejectDTO,
  OvertimeRequestDTO,
} from "~/api/hr_admin/overtime/dto";
import { ROUTES } from "~/constants/routes";
import { useOvertimeStore } from "~/stores/overtimeStore";

definePageMeta({ layout: "default" });

const router = useRouter();
const overtimeStore = useOvertimeStore();
const overtimeService = hrmsAdminService().overtimeRequest;

const searchEmployeeId = ref("");
const startDate = ref("");
const endDate = ref("");

const detailDialogVisible = ref(false);
const approveDialogVisible = ref(false);
const rejectDialogVisible = ref(false);

const approveFormRef = ref<FormInstance>();
const rejectFormRef = ref<FormInstance>();

const activeRequest = ref<OvertimeRequestDTO | null>(null);

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

const pendingRequests = computed(() => overtimeStore.pendingApproval);
const isLoadingQueue = computed(() =>
  overtimeStore.isLoading("getPendingRequests"),
);
const isLoadingDetail = computed(() => overtimeStore.isLoading("getRequest"));
const isLoadingApprove = computed(() =>
  overtimeStore.isLoading("approveRequest"),
);
const isLoadingReject = computed(() =>
  overtimeStore.isLoading("rejectRequest"),
);

const queueStats = computed(() => {
  const items = pendingRequests.value;
  const uniqueEmployees = new Set(items.map((row) => row.employee_id)).size;
  const averageHours = items.length
    ? items.reduce((total, row) => total + estimateHours(row), 0) / items.length
    : 0;

  return [
    {
      label: "Pending queue",
      value: overtimeStore.pagination.total,
      hint: "All requests returned by the pending-approval endpoint",
    },
    {
      label: "On this page",
      value: items.length,
      hint: "Visible rows in the current queue page",
    },
    {
      label: "Employees",
      value: uniqueEmployees,
      hint: "Unique employee IDs on this page",
    },
    {
      label: "Average hours",
      value: Number(averageHours.toFixed(1)),
      hint: "Estimated from start and end time when needed",
    },
  ];
});

const paginationProps = computed(() => ({
  currentPage: overtimeStore.pagination.page,
  pageSize: overtimeStore.pagination.limit,
  total: overtimeStore.pagination.total,
}));

const currentDetail = computed(() => {
  const requestDetail = overtimeStore.requestDetail;

  if (
    requestDetail?.id &&
    activeRequest.value?.id &&
    requestDetail.id === activeRequest.value.id
  ) {
    return requestDetail;
  }

  return activeRequest.value;
});

const hasFilters = computed(() =>
  Boolean(searchEmployeeId.value.trim() || startDate.value || endDate.value),
);

function normalizeDateInput(value: string): string {
  return String(value || "").trim();
}

function formatDate(value?: string | null): string {
  if (!value) return "—";

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
  if (!value) return "—";
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

function formatTime(value?: string | null): string {
  if (!value) return "—";

  if (/^\d{2}:\d{2}(:\d{2})?$/.test(value)) {
    return value.slice(0, 5);
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);

  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatMoney(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "—";
  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
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

function dayTypeLabel(dayType?: string | null): string {
  const map: Record<string, string> = {
    working_day: "Working Day",
    weekend: "Weekend",
    public_holiday: "Public Holiday",
  };

  return map[String(dayType || "").toLowerCase()] || "Unknown";
}

function estimateHours(row: OvertimeRequestDTO): number {
  if (Number.isFinite(Number(row.approved_hours)) && row.approved_hours > 0) {
    return Number(row.approved_hours.toFixed(2));
  }

  const start = new Date(row.start_time);
  const end = new Date(row.end_time);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 0;

  const hours = (end.getTime() - start.getTime()) / 3_600_000;
  return hours > 0 ? Number(hours.toFixed(2)) : 0;
}

function buildFilters() {
  return {
    employee_id: searchEmployeeId.value.trim() || undefined,
    start_date: normalizeDateInput(startDate.value) || undefined,
    end_date: normalizeDateInput(endDate.value) || undefined,
  };
}

async function fetchQueue(page = 1) {
  overtimeStore.setPagination(page, paginationProps.value.pageSize);
  overtimeStore.setFilters(buildFilters());

  try {
    await overtimeStore.fetchPendingApproval(page);
  } catch {
    ElMessage.error("Failed to load overtime review queue");
  }
}

function resetFilters() {
  searchEmployeeId.value = "";
  startDate.value = "";
  endDate.value = "";
  fetchQueue(1);
}

function openDetailDialog(row: OvertimeRequestDTO) {
  activeRequest.value = row;
  overtimeStore.clearDetail();
  detailDialogVisible.value = true;
  void loadDetail(row.id);
}

async function loadDetail(id: string) {
  try {
    await overtimeStore.fetchOne(id);
  } catch {
    if (!activeRequest.value) {
      ElMessage.error("Failed to load request details");
    }
  }
}

function closeDetailDialog() {
  detailDialogVisible.value = false;
  overtimeStore.clearDetail();
  activeRequest.value = null;
}

function openApproveDialog(row: OvertimeRequestDTO) {
  activeRequest.value = row;
  approveForm.approved_hours = estimateHours(row) || 1;
  approveForm.comment = null;
  approveDialogVisible.value = true;
}

function closeApproveDialog() {
  approveDialogVisible.value = false;
  approveForm.approved_hours = 0;
  approveForm.comment = null;
  activeRequest.value = null;
  approveFormRef.value?.clearValidate();
}

function openRejectDialog(row: OvertimeRequestDTO) {
  activeRequest.value = row;
  rejectForm.comment = "";
  rejectDialogVisible.value = true;
}

function closeRejectDialog() {
  rejectDialogVisible.value = false;
  rejectForm.comment = "";
  activeRequest.value = null;
  rejectFormRef.value?.clearValidate();
}

async function submitApprove() {
  if (!activeRequest.value) return;

  try {
    await approveFormRef.value?.validate();
  } catch {
    ElMessage.error("Please complete the approval form");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `Approve ${
        activeRequest.value.employee_id
      }'s overtime for ${approveForm.approved_hours.toFixed(2)} hours?`,
      "Confirm Approval",
      {
        confirmButtonText: "Approve",
        cancelButtonText: "Cancel",
        type: "success",
      },
    );

    await overtimeStore.approveRequest(activeRequest.value.id, {
      approved_hours: Number(approveForm.approved_hours),
      comment: String(approveForm.comment || "").trim() || null,
    });

    ElMessage.success("Overtime request approved");
    closeApproveDialog();
    await fetchQueue(paginationProps.value.currentPage);
  } catch (error: any) {
    if (error === "cancel") return;
    ElMessage.error(
      overtimeStore.getError("approveRequest") || "Failed to approve request",
    );
  }
}

async function submitReject() {
  if (!activeRequest.value) return;

  try {
    await rejectFormRef.value?.validate();
  } catch {
    ElMessage.error("Please add a rejection comment");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `Reject overtime request from ${activeRequest.value.employee_id}?`,
      "Confirm Rejection",
      {
        confirmButtonText: "Reject",
        cancelButtonText: "Cancel",
        type: "warning",
      },
    );

    await overtimeStore.rejectRequest(activeRequest.value.id, {
      comment: String(rejectForm.comment || "").trim(),
    });

    ElMessage.success("Overtime request rejected");
    closeRejectDialog();
    await fetchQueue(paginationProps.value.currentPage);
  } catch (error: any) {
    if (error === "cancel") return;
    ElMessage.error(
      overtimeStore.getError("rejectRequest") || "Failed to reject request",
    );
  }
}

async function handlePageChange(page: number) {
  await fetchQueue(page);
}

async function handlePageSizeChange(size: number) {
  overtimeStore.setPagination(1, size);
  await fetchQueue(1);
}

function applyFilters() {
  void fetchQueue(1);
}

function refreshQueue() {
  void fetchQueue(paginationProps.value.currentPage || 1);
}

import { onMounted } from "vue";
onMounted(() => {
  fetchQueue(1);
});
</script>

<template>
  <div class="overtime-reviews-page">
    <OverviewHeader
      title="Overtime Reviews"
      description="Pending OT review queue for HR approval or rejection"
    >
      <template #actions>
        <BaseButton
          plain
          :loading="isLoadingQueue"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="refreshQueue"
        >
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="isLoadingQueue"
          @click="router.push(ROUTES.HR_ADMIN.OVERTIME)"
        >
          Back
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="queue-stats">
      <el-col
        v-for="stat in queueStats"
        :key="stat.label"
        :xs="24"
        :sm="12"
        :lg="6"
      >
        <el-card class="queue-stat-card" shadow="never">
          <p class="queue-stat-card__label">{{ stat.label }}</p>
          <p class="queue-stat-card__value">{{ stat.value }}</p>
          <p class="queue-stat-card__hint">{{ stat.hint }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="queue-card" shadow="never">
      <template #header>
        <div class="queue-card__header">
          <div>
            <h2 class="queue-card__title">Pending Queue</h2>
            <p class="queue-card__subtitle">
              Each row can be reviewed, approved, or rejected.
            </p>
          </div>

          <div class="queue-card__actions">
            <span class="queue-card__count">
              {{ paginationProps.total }} total pending
            </span>
          </div>
        </div>
      </template>

      <el-row :gutter="12" class="filter-grid">
        <el-col :xs="24" :md="10">
          <el-input
            v-model="searchEmployeeId"
            clearable
            placeholder="Search by employee ID"
            @keyup.enter="applyFilters"
          />
        </el-col>

        <el-col :xs="24" :md="7">
          <el-date-picker
            v-model="startDate"
            class="w-full"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="Start date"
          />
        </el-col>

        <el-col :xs="24" :md="7">
          <el-date-picker
            v-model="endDate"
            class="w-full"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="End date"
          />
        </el-col>
      </el-row>

      <div class="filter-actions">
        <BaseButton
          type="primary"
          :loading="isLoadingQueue"
          @click="applyFilters"
        >
          Apply Filters
        </BaseButton>

        <BaseButton
          plain
          :disabled="isLoadingQueue || !hasFilters"
          @click="resetFilters"
        >
          Reset
        </BaseButton>
      </div>

      <div class="table-shell" v-loading="isLoadingQueue">
        <el-empty
          v-if="!isLoadingQueue && pendingRequests.length === 0"
          description="No pending overtime requests found"
        />

        <el-table v-else :data="pendingRequests" stripe class="queue-table">
          <el-table-column label="Employee" min-width="180">
            <template #default="{ row }">
              <div class="employee-cell">
                <span class="employee-cell__primary">{{
                  row.employee_id
                }}</span>
                <span class="employee-cell__secondary">{{ row.id }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="Request Date" min-width="130">
            <template #default="{ row }">
              {{ formatDate(row.request_date) }}
            </template>
          </el-table-column>

          <el-table-column label="Time Range" min-width="170">
            <template #default="{ row }">
              {{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}
            </template>
          </el-table-column>

          <el-table-column label="Hours" width="110">
            <template #default="{ row }">
              {{ estimateHours(row).toFixed(2) }}h
            </template>
          </el-table-column>

          <el-table-column label="Day Type" min-width="150">
            <template #default="{ row }">
              <ElTag effect="plain" round size="small" class="day-type-pill">
                {{ dayTypeLabel(row.day_type) }}
              </ElTag>
            </template>
          </el-table-column>

          <el-table-column label="Reason" min-width="260">
            <template #default="{ row }">
              <span class="reason-cell">{{ row.reason }}</span>
            </template>
          </el-table-column>

          <el-table-column label="Submitted" min-width="170">
            <template #default="{ row }">
              {{ formatDateTime(row.submitted_at) }}
            </template>
          </el-table-column>

          <el-table-column label="Status" width="130">
            <template #default="{ row }">
              <ElTag
                :type="statusTagType(row.status)"
                effect="plain"
                round
                size="small"
                :class="statusClass(row.status)"
              >
                {{
                  String(row.status || "-")
                    .charAt(0)
                    .toUpperCase() + String(row.status || "-").slice(1)
                }}
              </ElTag>
            </template>
          </el-table-column>

          <el-table-column
            label="Actions"
            width="240"
            fixed="right"
            align="center"
          >
            <template #default="{ row }">
              <ElButton
                link
                type="primary"
                size="small"
                @click="openDetailDialog(row)"
              >
                View
              </ElButton>
              <ElButton
                link
                type="success"
                size="small"
                @click="openApproveDialog(row)"
              >
                Approve
              </ElButton>
              <ElButton
                link
                type="danger"
                size="small"
                @click="openRejectDialog(row)"
              >
                Reject
              </ElButton>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="paginationProps.total > 0" class="pagination-row">
        <ElPagination
          :current-page="paginationProps.currentPage"
          :page-size="paginationProps.pageSize"
          :total="paginationProps.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <ElDialog
      v-model="detailDialogVisible"
      title="Overtime Request Details"
      width="760px"
      @close="closeDetailDialog"
    >
      <div v-loading="isLoadingDetail">
        <template v-if="currentDetail">
          <div class="detail-head">
            <div>
              <h3 class="detail-head__title">
                {{ currentDetail.employee_id }}
              </h3>
              <p class="detail-head__subtitle">
                Request {{ currentDetail.id }}
              </p>
            </div>

            <ElTag
              :type="statusTagType(currentDetail.status)"
              effect="plain"
              round
              size="small"
              :class="statusClass(currentDetail.status)"
            >
              {{
                String(currentDetail.status || "-")
                  .charAt(0)
                  .toUpperCase() + String(currentDetail.status || "-").slice(1)
              }}
            </ElTag>
          </div>

          <ElDescriptions :column="2" border class="mt-4">
            <ElDescriptionsItem label="Employee ID">
              {{ currentDetail.employee_id }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Request Date">
              {{ formatDate(currentDetail.request_date) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Start Time">
              {{ formatDateTime(currentDetail.start_time) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="End Time">
              {{ formatDateTime(currentDetail.end_time) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Submitted At">
              {{ formatDateTime(currentDetail.submitted_at) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Day Type">
              {{ dayTypeLabel(currentDetail.day_type) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Approved Hours">
              {{ Number(currentDetail.approved_hours || 0).toFixed(2) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Calculated Payment">
              {{ formatMoney(currentDetail.calculated_payment) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Basic Salary">
              {{ formatMoney(currentDetail.basic_salary) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Manager ID">
              {{ currentDetail.manager_id || "—" }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Reason" :span="2">
              {{ currentDetail.reason }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Manager Comment" :span="2">
              {{ currentDetail.manager_comment || "—" }}
            </ElDescriptionsItem>
          </ElDescriptions>
        </template>

        <ElEmpty v-else description="No overtime request details available" />
      </div>
    </ElDialog>

    <ElDialog
      v-model="approveDialogVisible"
      title="Approve Overtime Request"
      width="560px"
      @close="closeApproveDialog"
    >
      <template v-if="activeRequest">
        <div class="dialog-summary">
          <div>
            <p class="dialog-summary__label">Employee</p>
            <p class="dialog-summary__value">{{ activeRequest.employee_id }}</p>
          </div>
          <div>
            <p class="dialog-summary__label">Suggested hours</p>
            <p class="dialog-summary__value">
              {{ estimateHours(activeRequest).toFixed(2) }}h
            </p>
          </div>
        </div>

        <ElForm
          ref="approveFormRef"
          :model="approveForm"
          :rules="approveRules"
          label-width="130px"
        >
          <ElFormItem label="Approved Hours" prop="approved_hours">
            <ElInputNumber
              v-model="approveForm.approved_hours"
              class="w-full"
              :min="0.25"
              :max="24"
              :step="0.25"
              :precision="2"
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
      </template>

      <template #footer>
        <ElButton @click="closeApproveDialog">Cancel</ElButton>
        <ElButton
          type="success"
          :loading="isLoadingApprove"
          @click="submitApprove"
        >
          Approve
        </ElButton>
      </template>
    </ElDialog>

    <ElDialog
      v-model="rejectDialogVisible"
      title="Reject Overtime Request"
      width="560px"
      @close="closeRejectDialog"
    >
      <template v-if="activeRequest">
        <div class="dialog-summary">
          <div>
            <p class="dialog-summary__label">Employee</p>
            <p class="dialog-summary__value">{{ activeRequest.employee_id }}</p>
          </div>
          <div>
            <p class="dialog-summary__label">Request date</p>
            <p class="dialog-summary__value">
              {{ formatDate(activeRequest.request_date) }}
            </p>
          </div>
        </div>

        <ElForm
          ref="rejectFormRef"
          :model="rejectForm"
          :rules="rejectRules"
          label-width="130px"
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
      </template>

      <template #footer>
        <ElButton @click="closeRejectDialog">Cancel</ElButton>
        <ElButton
          type="danger"
          :loading="isLoadingReject"
          @click="submitReject"
        >
          Reject
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.overtime-reviews-page {
  padding: 20px;
  max-width: 1520px;
  margin: 0 auto;
}

.queue-stats {
  margin-bottom: 16px;
}

.queue-stat-card {
  border-radius: 16px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, white 18%);
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  height: 100%;
}

.queue-stat-card__label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #7a7f89;
}

.queue-stat-card__value {
  margin: 8px 0 4px;
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--color-dark);
}

.queue-stat-card__hint {
  margin: 0;
  font-size: 12px;
  color: #808694;
}

.queue-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, white 18%);
  box-shadow: 0 14px 36px rgba(16, 24, 40, 0.06);
}

.queue-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.queue-card__title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-dark);
}

.queue-card__subtitle {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.queue-card__count {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary-light-8) 70%, white 30%);
  color: var(--color-primary);
  font-size: 12px;
  font-weight: 700;
}

.filter-grid {
  margin-bottom: 12px;
}

.filter-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.table-shell {
  min-height: 220px;
}

.queue-table {
  width: 100%;
}

.employee-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.employee-cell__primary {
  font-weight: 700;
  color: var(--color-dark);
}

.employee-cell__secondary {
  font-size: 12px;
  color: #81868f;
  word-break: break-all;
}

.reason-cell {
  display: block;
  line-height: 1.5;
  color: var(--color-dark);
}

.day-type-pill,
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

.pagination-row {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.detail-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.detail-head__title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-dark);
}

.detail-head__subtitle {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.dialog-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 14px;
  background: color-mix(in srgb, var(--color-primary-light-9) 78%, white 22%);
}

.dialog-summary__label {
  margin: 0 0 4px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #7a7f89;
}

.dialog-summary__value {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-dark);
}

@media (max-width: 768px) {
  .queue-card__header,
  .detail-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .dialog-summary {
    grid-template-columns: 1fr;
  }

  .pagination-row {
    justify-content: flex-start;
  }
}
</style>
