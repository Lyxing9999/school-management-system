<script setup lang="ts">
import { computed, onActivated, onMounted, reactive, ref } from "vue";
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
  ElMessage,
  ElPagination,
  ElRow,
  ElSelect,
  ElOption,
  ElTable,
  ElTableColumn,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  LeaveApproveDTO,
  LeaveRejectDTO,
  LeaveRequestDTO,
  LeaveRequestStatus,
  LeaveType,
} from "~/api/hr_admin/leave/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const router = useRouter();
const leaveService = hrmsAdminService().leaveRequest;

const searchEmployeeId = ref("");
const leaveTypeFilter = ref<LeaveType | "">("");
const startDate = ref("");
const endDate = ref("");

const loadingQueue = ref(false);
const loadingDetail = ref(false);
const actionLoading = ref(false);

const rows = ref<LeaveRequestDTO[]>([]);
const detailRecord = ref<LeaveRequestDTO | null>(null);
const activeRequest = ref<LeaveRequestDTO | null>(null);

const detailDialogVisible = ref(false);
const approveDialogVisible = ref(false);
const rejectDialogVisible = ref(false);

const approveFormRef = ref<FormInstance>();
const rejectFormRef = ref<FormInstance>();

const approveForm = reactive<LeaveApproveDTO>({
  comment: null,
});

const rejectForm = reactive<LeaveRejectDTO>({
  comment: "",
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
        const normalized = String(value || "").trim();
        if (!normalized) {
          callback(new Error("Rejection comment is required"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
};

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});
const initialized = ref(false);

const filteredRows = computed(() => {
  const keyword = searchEmployeeId.value.trim().toLowerCase();
  const leaveType = leaveTypeFilter.value.trim().toLowerCase();

  return rows.value.filter((row) => {
    const byEmployee = keyword
      ? String(displayRelation(row.employee_name, row.employee_id))
          .toLowerCase()
          .includes(keyword)
      : true;

    const byLeaveType = leaveType
      ? String(row.leave_type || "").toLowerCase() === leaveType
      : true;

    const byStartDate = startDate.value
      ? String(row.start_date || "") >= startDate.value
      : true;

    const byEndDate = endDate.value
      ? String(row.end_date || "") <= endDate.value
      : true;

    return byEmployee && byLeaveType && byStartDate && byEndDate;
  });
});

const queueStats = computed(() => {
  const items = filteredRows.value;
  const uniqueEmployees = new Set(items.map((row) => row.employee_id)).size;
  const totalDays = items.reduce(
    (acc, row) => acc + Number(row.total_days || 0),
    0,
  );
  const avgDays = items.length ? totalDays / items.length : 0;

  return [
    {
      label: "Pending queue",
      value: pagination.total,
      hint: "All leave requests returned by pending-reviews endpoint",
    },
    {
      label: "On this page",
      value: items.length,
      hint: "Visible rows after current filters",
    },
    {
      label: "Employees",
      value: uniqueEmployees,
      hint: "Unique employee IDs in current result",
    },
    {
      label: "Average days",
      value: Number(avgDays.toFixed(1)),
      hint: "Average requested leave days",
    },
  ];
});

const paginationProps = computed(() => ({
  currentPage: pagination.page,
  pageSize: pagination.limit,
  total: pagination.total,
}));

const hasFilters = computed(() =>
  Boolean(
    searchEmployeeId.value.trim() ||
      leaveTypeFilter.value ||
      startDate.value ||
      endDate.value,
  ),
);

function leaveTypeLabel(value?: string | null): string {
  if (!value) return "-";

  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

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
  status?: LeaveRequestStatus | string | null,
): "warning" | "success" | "danger" | "info" {
  const map: Record<string, "warning" | "success" | "danger" | "info"> = {
    pending: "warning",
    approved: "success",
    rejected: "danger",
    cancelled: "info",
  };

  return map[String(status || "").toLowerCase()] || "info";
}

function statusClass(status?: LeaveRequestStatus | string | null): string {
  const map: Record<string, string> = {
    pending: "status-pill status-pill--pending",
    approved: "status-pill status-pill--approved",
    rejected: "status-pill status-pill--rejected",
    cancelled: "status-pill status-pill--cancelled",
  };

  return map[String(status || "").toLowerCase()] || "status-pill";
}

function closeDetailDialog() {
  detailDialogVisible.value = false;
  detailRecord.value = null;
  activeRequest.value = null;
}

async function fetchQueue(page = 1, limit = pagination.limit) {
  loadingQueue.value = true;
  try {
    const response = await leaveService.getPendingRequests({
      page,
      limit,
      employee_id: searchEmployeeId.value.trim() || undefined,
      status: "pending",
      start_date: startDate.value || undefined,
      end_date: endDate.value || undefined,
    });

    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.page_size ?? limit;
  } catch {
    // API layer already emits user-friendly error notifications.
  } finally {
    loadingQueue.value = false;
  }
}

function applyFilters() {
  pagination.page = 1;
  void fetchQueue(1, pagination.limit);
}

function resetFilters() {
  searchEmployeeId.value = "";
  leaveTypeFilter.value = "";
  startDate.value = "";
  endDate.value = "";
  pagination.page = 1;
  void fetchQueue(1, pagination.limit);
}

function openDetailDialog(row: LeaveRequestDTO) {
  activeRequest.value = row;
  detailRecord.value = row;
  detailDialogVisible.value = true;
  void loadDetail(row.id);
}

async function loadDetail(id: string) {
  loadingDetail.value = true;
  try {
    detailRecord.value = await leaveService.getRequest(id);
  } catch {
    // API layer already emits user-friendly error notifications.
  } finally {
    loadingDetail.value = false;
  }
}

function openApproveDialog(row: LeaveRequestDTO) {
  activeRequest.value = row;
  approveForm.comment = null;
  approveDialogVisible.value = true;
}

function closeApproveDialog() {
  approveDialogVisible.value = false;
  approveForm.comment = null;
  activeRequest.value = null;
  approveFormRef.value?.clearValidate();
}

function openRejectDialog(row: LeaveRequestDTO) {
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
    ElMessage.error("Please check the approval form");
    return;
  }

  try {
    actionLoading.value = true;
    await leaveService.approveRequest(activeRequest.value.id, {
      comment: normalizeComment(approveForm.comment),
    });

    closeApproveDialog();
    await fetchQueue(pagination.page, pagination.limit);
  } catch {
    // API layer already emits user-friendly error notifications.
  } finally {
    actionLoading.value = false;
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
    actionLoading.value = true;
    const normalizedRejectComment = normalizeComment(rejectForm.comment);
    if (!normalizedRejectComment) {
      ElMessage.error("Please add a rejection comment");
      return;
    }

    await leaveService.rejectRequest(activeRequest.value.id, {
      comment: normalizedRejectComment,
    });

    closeRejectDialog();
    await fetchQueue(pagination.page, pagination.limit);
  } catch {
    // API layer already emits user-friendly error notifications.
  } finally {
    actionLoading.value = false;
  }
}

async function handlePageChange(page: number) {
  await fetchQueue(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchQueue(1, size);
}

function refreshQueue() {
  void fetchQueue(pagination.page, pagination.limit);
}

function normalizeComment(value?: string | null): string | null {
  const normalized = String(value || "").trim();
  return normalized || null;
}

async function ensureInitialLoad() {
  if (initialized.value) return;
  initialized.value = true;
  await fetchQueue(1, pagination.limit);
}

onMounted(() => {
  void ensureInitialLoad();
});

onActivated(() => {
  // Keep data fresh when returning to this route from another page.
  void fetchQueue(pagination.page, pagination.limit);
});
</script>

<template>
  <div class="leave-reviews-page">
    <OverviewHeader
      title="Leave Reviews"
      description="Pending leave review queue for HR approval or rejection"
    >
      <template #actions>
        <BaseButton
          plain
          :loading="loadingQueue"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="refreshQueue"
        >
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loadingQueue"
          @click="router.push(ROUTES.HR_ADMIN.LEAVES)"
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
            <span class="queue-card__count"
              >{{ paginationProps.total }} total pending</span
            >
          </div>
        </div>
      </template>

      <el-row :gutter="12" class="filter-grid">
        <el-col :xs="24" :md="8">
          <el-input
            v-model="searchEmployeeId"
            clearable
            placeholder="Search by employee"
            @keyup.enter="applyFilters"
          />
        </el-col>

        <el-col :xs="24" :md="6">
          <ElSelect
            v-model="leaveTypeFilter"
            clearable
            class="w-full"
            placeholder="Leave type"
          >
            <ElOption label="Annual" value="annual" />
            <ElOption label="Sick" value="sick" />
            <ElOption label="Unpaid" value="unpaid" />
            <ElOption label="Other" value="other" />
          </ElSelect>
        </el-col>

        <el-col :xs="24" :md="5">
          <el-date-picker
            v-model="startDate"
            class="w-full"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="Start date"
          />
        </el-col>

        <el-col :xs="24" :md="5">
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
          :loading="loadingQueue"
          @click="applyFilters"
        >
          Apply Filters
        </BaseButton>

        <BaseButton
          plain
          :disabled="loadingQueue || !hasFilters"
          @click="resetFilters"
        >
          Reset
        </BaseButton>
      </div>

      <div class="table-shell" v-loading="loadingQueue">
        <el-empty
          v-if="!loadingQueue && filteredRows.length === 0"
          description="No pending leave requests found"
        />

        <el-table v-else :data="filteredRows" stripe class="queue-table">
          <el-table-column label="Employee" min-width="180">
            <template #default="{ row }">
              <div class="employee-cell">
                <span class="employee-cell__primary">{{
                  displayRelation(row.employee_name, row.employee_id)
                }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="Leave Type" min-width="140">
            <template #default="{ row }">
              {{ leaveTypeLabel(row.leave_type) }}
            </template>
          </el-table-column>

          <el-table-column label="Start Date" min-width="130">
            <template #default="{ row }">
              {{ formatDate(row.start_date) }}
            </template>
          </el-table-column>

          <el-table-column label="End Date" min-width="130">
            <template #default="{ row }">
              {{ formatDate(row.end_date) }}
            </template>
          </el-table-column>

          <el-table-column label="Days" width="90">
            <template #default="{ row }">
              {{ Number(row.total_days || 0).toFixed(1) }}
            </template>
          </el-table-column>

          <el-table-column label="Paid" width="90">
            <template #default="{ row }">
              <ElTag
                :type="row.is_paid ? 'success' : 'info'"
                effect="plain"
                round
                size="small"
              >
                {{ row.is_paid ? "Yes" : "No" }}
              </ElTag>
            </template>
          </el-table-column>

          <el-table-column label="Reason" min-width="260">
            <template #default="{ row }">
              <span class="reason-cell">{{ row.reason }}</span>
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
      title="Leave Request Details"
      width="760px"
      @close="closeDetailDialog"
    >
      <div v-loading="loadingDetail">
        <template v-if="detailRecord">
          <div class="detail-head">
            <div>
              <h3 class="detail-head__title">
                {{ displayRelation(detailRecord.employee_name, detailRecord.employee_id) }}
              </h3>
            </div>

            <ElTag
              :type="statusTagType(detailRecord.status)"
              effect="plain"
              round
              size="small"
              :class="statusClass(detailRecord.status)"
            >
              {{
                String(detailRecord.status || "-")
                  .charAt(0)
                  .toUpperCase() + String(detailRecord.status || "-").slice(1)
              }}
            </ElTag>
          </div>

          <ElDescriptions :column="2" border class="mt-4">
            <ElDescriptionsItem label="Employee">
              {{
                displayRelation(detailRecord.employee_name, detailRecord.employee_id)
              }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Leave Type">
              {{ leaveTypeLabel(detailRecord.leave_type) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Start Date">
              {{ formatDate(detailRecord.start_date) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="End Date">
              {{ formatDate(detailRecord.end_date) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Total Days">
              {{ Number(detailRecord.total_days || 0).toFixed(1) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Paid Leave">
              {{ detailRecord.is_paid ? "Yes" : "No" }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Contract Start">
              {{ formatDate(detailRecord.contract_start) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Contract End">
              {{ formatDate(detailRecord.contract_end) }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Manager">
              {{
                displayRelation(detailRecord.manager_name, detailRecord.manager_user_id)
              }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Reason" :span="2">
              {{ detailRecord.reason }}
            </ElDescriptionsItem>
            <ElDescriptionsItem label="Manager Comment" :span="2">
              {{ detailRecord.manager_comment || "-" }}
            </ElDescriptionsItem>
          </ElDescriptions>
        </template>

        <ElEmpty v-else description="No leave request details available" />
      </div>
    </ElDialog>

    <ElDialog
      v-model="approveDialogVisible"
      title="Approve Leave Request"
      width="560px"
      @close="closeApproveDialog"
    >
      <template v-if="activeRequest">
        <div class="dialog-summary">
          <div>
            <p class="dialog-summary__label">Employee</p>
            <p class="dialog-summary__value">
              {{ displayRelation(activeRequest.employee_name, activeRequest.employee_id) }}
            </p>
          </div>
          <div>
            <p class="dialog-summary__label">Requested Days</p>
            <p class="dialog-summary__value">
              {{ Number(activeRequest.total_days || 0).toFixed(1) }} days
            </p>
          </div>
        </div>

        <ElForm
          ref="approveFormRef"
          :model="approveForm"
          :rules="approveRules"
          label-width="130px"
        >
          <ElFormItem label="Comment" prop="comment">
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
      width="560px"
      @close="closeRejectDialog"
    >
      <template v-if="activeRequest">
        <div class="dialog-summary">
          <div>
            <p class="dialog-summary__label">Employee</p>
            <p class="dialog-summary__value">
              {{ displayRelation(activeRequest.employee_name, activeRequest.employee_id) }}
            </p>
          </div>
          <div>
            <p class="dialog-summary__label">Leave Type</p>
            <p class="dialog-summary__value">
              {{ leaveTypeLabel(activeRequest.leave_type) }}
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
        <ElButton type="danger" :loading="actionLoading" @click="submitReject">
          Reject
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.leave-reviews-page {
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
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  background: linear-gradient(
    180deg,
    var(--color-card) 0%,
    color-mix(in srgb, var(--hover-bg) 28%, var(--color-card) 72%) 100%
  );
  height: 100%;
}

.queue-stat-card__label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted-color);
}

.queue-stat-card__value {
  margin: 8px 0 4px;
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--text-color);
}

.queue-stat-card__hint {
  margin: 0;
  font-size: 12px;
  color: var(--muted-color);
  line-height: 1.35;
}

.queue-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  box-shadow: 0 14px 36px var(--card-shadow);
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
  color: var(--text-color);
}

.queue-card__subtitle {
  margin: 4px 0 0;
  color: var(--muted-color);
  font-size: 13px;
}

.queue-card__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.queue-card__count {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: color-mix(
    in srgb,
    var(--color-primary-light-8) 70%,
    var(--color-card) 30%
  );
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
  color: var(--text-color);
}

.employee-cell__secondary {
  font-size: 12px;
  color: var(--muted-color);
  word-break: break-all;
}

.reason-cell {
  display: block;
  line-height: 1.5;
  color: var(--text-color);
}

.status-pill {
  font-weight: 650;
  letter-spacing: 0.01em;
}

.status-pill--pending {
  border-color: color-mix(
    in srgb,
    var(--button-warning-bg) 55%,
    var(--border-color) 45%
  );
  color: var(--button-warning-bg);
  background: color-mix(
    in srgb,
    var(--button-warning-bg) 18%,
    var(--color-card) 82%
  );
}

.status-pill--approved {
  border-color: color-mix(
    in srgb,
    var(--button-success-bg) 55%,
    var(--border-color) 45%
  );
  color: var(--button-success-bg);
  background: color-mix(
    in srgb,
    var(--button-success-bg) 18%,
    var(--color-card) 82%
  );
}

.status-pill--rejected {
  border-color: color-mix(
    in srgb,
    var(--button-danger-bg) 55%,
    var(--border-color) 45%
  );
  color: var(--button-danger-bg);
  background: color-mix(
    in srgb,
    var(--button-danger-bg) 18%,
    var(--color-card) 82%
  );
}

.status-pill--cancelled {
  border-color: color-mix(
    in srgb,
    var(--muted-color) 45%,
    var(--border-color) 55%
  );
  color: var(--muted-color);
  background: var(--hover-bg);
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
  color: var(--text-color);
}

.detail-head__subtitle {
  margin: 4px 0 0;
  color: var(--muted-color);
  font-size: 13px;
}

.dialog-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  padding: 12px;
  border-radius: 12px;
  background: var(--hover-bg);
  border: 1px solid var(--border-color);
  margin-bottom: 14px;
}

.dialog-summary__label {
  margin: 0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted-color);
}

.dialog-summary__value {
  margin: 4px 0 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-color);
}

@media (max-width: 768px) {
  .queue-card__header,
  .detail-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination-row {
    justify-content: flex-start;
  }

  .dialog-summary {
    grid-template-columns: 1fr;
  }
}
</style>
