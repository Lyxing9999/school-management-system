<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import {
  ElButton,
  ElCol,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElOption,
  ElPagination,
  ElRow,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type { AttendanceDTO } from "~/api/hr_admin/attendance";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import type { ColumnConfig } from "~/components/types/tableEdit";

definePageMeta({ layout: "default" });

type ReviewAction = "approve" | "reject";
type StatusFilter = "all" | "pending" | "approved" | "rejected";

const attendanceService = hrmsAdminService().attendance;

const query = ref("");
const statusFilter = ref<StatusFilter>("pending");
const rows = ref<AttendanceDTO[]>([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const totalRows = ref(0);

const reviewDialogVisible = ref(false);
const reviewAction = ref<ReviewAction>("approve");
const reviewLoading = ref(false);
const activeRow = ref<AttendanceDTO | null>(null);
const reviewFormRef = ref<FormInstance>();
const reviewForm = reactive({
  comment: "",
});

const reviewRules: FormRules = {
  comment: [
    {
      validator: (_rule, value: string, callback) => {
        if (reviewAction.value === "reject" && !String(value || "").trim()) {
          callback(new Error("Comment is required when rejecting"));
          return;
        }
        callback();
      },
      trigger: "blur",
    },
  ],
};

const tableColumns: ColumnConfig<AttendanceDTO>[] = [
  {
    field: "employee_id",
    label: "Employee",
    minWidth: "140px",
    visible: true,
    render: (row: AttendanceDTO) =>
      displayRelation(row.employee_name, row.employee_id),
  },
  {
    field: "attendance_date",
    label: "Attendance Date",
    width: "150px",
    visible: true,
    render: (row: AttendanceDTO) => formatDate(row.attendance_date),
  },
  {
    field: "check_out_time",
    label: "Check Out",
    width: "160px",
    visible: true,
    render: (row: AttendanceDTO) => formatDateTime(row.check_out_time),
  },
  {
    field: "early_leave_minutes",
    label: "Early Leave",
    width: "120px",
    visible: true,
    render: (row: AttendanceDTO) =>
      row.early_leave_minutes > 0 ? `${row.early_leave_minutes} min` : "-",
  },
  {
    field: "early_leave_reason",
    label: "Reason",
    minWidth: "220px",
    visible: true,
    render: (row: AttendanceDTO) => row.early_leave_reason || "-",
  },
  {
    field: "admin_comment",
    label: "Reviewer Comment",
    minWidth: "220px",
    visible: true,
    render: (row: AttendanceDTO) => row.admin_comment || "-",
  },
  {
    field: "status",
    label: "Status",
    width: "180px",
    visible: true,
    slotName: "status",
  },
  {
    field: "id",
    operation: true,
    label: "Actions",
    width: "260px",
    fixed: "right",
    visible: true,
    slotName: "operation",
  },
];

const filteredRows = computed(() => {
  const keyword = query.value.trim().toLowerCase();

  return rows.value.filter((row) => {
    const statusKey = normalizeEarlyLeaveStatus(earlyLeaveStatusKey(row));
    if (statusFilter.value !== "all" && statusKey !== statusFilter.value) {
      return false;
    }

    if (!keyword) return true;

    return (
      String(displayRelation(row.employee_name, row.employee_id))
        .toLowerCase()
        .includes(keyword) ||
      String(row.early_leave_reason || "")
        .toLowerCase()
        .includes(keyword) ||
      String(row.admin_comment || "")
        .toLowerCase()
        .includes(keyword)
    );
  });
});

const displayedTotal = computed(() => {
  if (query.value.trim()) return filteredRows.value.length;
  return totalRows.value;
});

function earlyLeaveStatusKey(row: AttendanceDTO): string {
  const reviewStatus = String(row.early_leave_review_status || "")
    .trim()
    .toLowerCase();
  if (reviewStatus === "pending") return "early_leave_pending";
  if (reviewStatus === "approved") return "early_leave_approved";
  if (reviewStatus === "rejected") return "early_leave_rejected";

  // Backward compatibility for legacy records that still use
  // status=early_leave without explicit review_status.
  if (
    String(row.status || "").trim().toLowerCase() === "early_leave" &&
    Number(row.early_leave_minutes || 0) > 0
  ) {
    return "early_leave_pending";
  }

  return String(row.status || "").trim().toLowerCase();
}

function normalizeEarlyLeaveStatus(status?: string | null): StatusFilter {
  const value = String(status || "").trim().toLowerCase();
  if (value === "early_leave_pending") return "pending";
  if (value === "early_leave_approved") return "approved";
  if (value === "early_leave_rejected") return "rejected";
  return "all";
}

function statusLabel(status?: string | null): string {
  const map: Record<string, string> = {
    early_leave_pending: "Pending",
    early_leave_approved: "Approved",
    early_leave_rejected: "Rejected",
    early_leave: "Early Leave",
  };
  return map[String(status || "").toLowerCase()] || "Unknown";
}

function isPendingEarlyLeave(status?: string | null): boolean {
  return String(status || "").toLowerCase() === "early_leave_pending";
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
  status?: string | null,
): "warning" | "success" | "danger" | "info" {
  const map: Record<string, "warning" | "success" | "danger" | "info"> = {
    early_leave_pending: "warning",
    early_leave_approved: "success",
    early_leave_rejected: "danger",
    early_leave: "warning",
  };
  return map[String(status || "").toLowerCase()] || "info";
}

function statusClass(status?: string | null): string {
  const map: Record<string, string> = {
    early_leave_pending: "status-pill status-pill--pending",
    early_leave_approved: "status-pill status-pill--approved",
    early_leave_rejected: "status-pill status-pill--rejected",
    early_leave: "status-pill status-pill--pending",
  };
  return map[String(status || "").toLowerCase()] || "status-pill";
}

async function fetchEarlyLeaveReports(page = currentPage.value) {
  loading.value = true;

  try {
    const response = await attendanceService.getEarlyLeaveReports(
      {
        page,
        limit: pageSize.value,
        review_status:
          statusFilter.value === "all" ? undefined : statusFilter.value,
      },
      { showError: false },
    );

    rows.value = response.items ?? [];
    const pagination = response.pagination;

    totalRows.value = pagination?.total ?? rows.value.length;
    currentPage.value = pagination?.page ?? page;
    pageSize.value = pagination?.page_size ?? pageSize.value;
  } catch {
    ElMessage.error("Failed to load early-leave reports");
  } finally {
    loading.value = false;
  }
}

function openReviewDialog(row: AttendanceDTO, action: ReviewAction) {
  if (!isPendingEarlyLeave(earlyLeaveStatusKey(row))) {
    ElMessageBox.alert(
      "Only pending early-leave cases can be reviewed",
      "Cannot Review",
      { type: "warning" },
    );
    return;
  }

  activeRow.value = row;
  reviewAction.value = action;
  reviewForm.comment = "";
  reviewDialogVisible.value = true;
}

async function submitReview() {
  if (!activeRow.value) return;

  await reviewFormRef.value?.validate();

  reviewLoading.value = true;
  try {
    await attendanceService.reviewEarlyLeave(
      activeRow.value.id,
      {
        approved: reviewAction.value === "approve",
        comment: reviewForm.comment.trim() || null,
      },
      { showSuccess: false, showError: false },
    );

    ElMessage.success(
      reviewAction.value === "approve"
        ? "Early-leave case approved"
        : "Early-leave case rejected",
    );

    reviewDialogVisible.value = false;
    activeRow.value = null;
    await fetchEarlyLeaveReports(currentPage.value);
  } catch (error) {
    ElMessage.error(mapError(error, "Failed to submit review action"));
  } finally {
    reviewLoading.value = false;
  }
}

function mapError(error: unknown, fallback: string) {
  if (error && typeof error === "object" && "response" in error) {
    const e = error as {
      response?: { data?: { user_message?: string; message?: string } };
    };
    return e.response?.data?.user_message || e.response?.data?.message || fallback;
  }

  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

async function showDetails(row: AttendanceDTO) {
  await ElMessageBox.alert(
    `Employee: ${displayRelation(
      row.employee_name,
      row.employee_id,
    )}\nAttendance Date: ${formatDate(
      row.attendance_date,
    )}\nCheck Out: ${formatDateTime(row.check_out_time)}\nStatus: ${statusLabel(
      earlyLeaveStatusKey(row),
    )}\nEarly leave: ${
      row.early_leave_minutes > 0 ? `${row.early_leave_minutes} min` : "-"
    }\nReason: ${row.early_leave_reason || "-"}\nReviewer comment: ${
      row.admin_comment || "-"
    }`,
    "Early-leave details",
    { type: "info" },
  );
}

const handleChangePageSize = async (size: number) => {
  pageSize.value = size;
  await fetchEarlyLeaveReports(1);
};

watch(statusFilter, async () => {
  await fetchEarlyLeaveReports(1);
});

onMounted(() => {
  fetchEarlyLeaveReports(1);
});
</script>

<template>
  <OverviewHeader
    :title="'Early Leave Reviews'"
    :description="'Review pending and completed early-leave attendance cases'"
    :backPath="'/manager/attendance/reports'"
  >
    <template #actions>
      <BaseButton
        plain
        :loading="loading"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="fetchEarlyLeaveReports(currentPage || 1)"
      >
        Refresh
      </BaseButton>
    </template>
  </OverviewHeader>

  <el-row :gutter="16" class="mb-4">
    <el-col :span="12">
      <el-input
        v-model="query"
        placeholder="Search employee, reason, comment"
        clearable
      />
    </el-col>
    <el-col :span="12">
      <el-select
        v-model="statusFilter"
        placeholder="Filter by status"
        class="w-full"
      >
        <el-option label="All" value="all" />
        <el-option label="Pending" value="pending" />
        <el-option label="Approved" value="approved" />
        <el-option label="Rejected" value="rejected" />
      </el-select>
    </el-col>
  </el-row>

  <SmartTable
    :columns="tableColumns"
    :data="filteredRows"
    :loading="loading"
    :total="displayedTotal"
    :page="currentPage"
    :page-size="pageSize"
    @page="fetchEarlyLeaveReports"
    @page-size="handleChangePageSize"
  >
    <template #status="{ row }">
      <el-tag
        :type="statusTagType(earlyLeaveStatusKey(row as AttendanceDTO))"
        effect="plain"
        round
        size="small"
        :class="statusClass(earlyLeaveStatusKey(row as AttendanceDTO))"
      >
        {{ statusLabel(earlyLeaveStatusKey(row as AttendanceDTO)) }}
      </el-tag>
    </template>

    <template #operation="{ row }">
      <el-space class="review-actions" :size="6">
        <template
          v-if="isPendingEarlyLeave(earlyLeaveStatusKey(row as AttendanceDTO))"
        >
          <el-button
            type="success"
            size="small"
            plain
            class="review-btn review-btn--approve"
            @click.stop="openReviewDialog(row as AttendanceDTO, 'approve')"
          >
            Approve
          </el-button>
          <el-button
            type="danger"
            size="small"
            plain
            class="review-btn review-btn--reject"
            @click.stop="openReviewDialog(row as AttendanceDTO, 'reject')"
          >
            Reject
          </el-button>
        </template>

        <el-button
          type="info"
          size="small"
          plain
          class="review-btn review-btn--view"
          @click.stop="showDetails(row as AttendanceDTO)"
        >
          View
        </el-button>
      </el-space>
    </template>
  </SmartTable>

  <el-row v-if="displayedTotal > 0" justify="end" class="m-4">
    <el-pagination
      :current-page="currentPage"
      :page-size="pageSize"
      :total="displayedTotal"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      background
      @current-change="fetchEarlyLeaveReports"
      @size-change="handleChangePageSize"
    />
  </el-row>

  <ElDialog
    v-model="reviewDialogVisible"
    :title="
      reviewAction === 'approve'
        ? 'Approve Early-Leave Case'
        : 'Reject Early-Leave Case'
    "
    width="520px"
  >
    <ElForm
      ref="reviewFormRef"
      :model="reviewForm"
      :rules="reviewRules"
      label-width="94px"
    >
      <ElFormItem label="Employee">
        <ElInput
          :model-value="
            displayRelation(activeRow?.employee_name, activeRow?.employee_id)
          "
          readonly
        />
      </ElFormItem>
      <ElFormItem label="Date">
        <ElInput
          :model-value="formatDate(activeRow?.attendance_date)"
          readonly
        />
      </ElFormItem>
      <ElFormItem label="Check Out">
        <ElInput
          :model-value="formatDateTime(activeRow?.check_out_time)"
          readonly
        />
      </ElFormItem>
      <ElFormItem label="Early Leave">
        <ElInput
          :model-value="
            activeRow && activeRow.early_leave_minutes > 0
              ? `${activeRow.early_leave_minutes} min`
              : '-'
          "
          readonly
        />
      </ElFormItem>
      <ElFormItem label="Reason">
        <ElInput
          :model-value="activeRow?.early_leave_reason || '-'"
          type="textarea"
          readonly
          :rows="3"
        />
      </ElFormItem>
      <ElFormItem label="Comment" prop="comment">
        <ElInput
          v-model="reviewForm.comment"
          type="textarea"
          :rows="3"
          :placeholder="
            reviewAction === 'approve'
              ? 'Optional approval comment'
              : 'Required rejection comment'
          "
        />
      </ElFormItem>
    </ElForm>

    <template #footer>
      <ElButton @click="reviewDialogVisible = false">Cancel</ElButton>
      <ElButton
        :type="reviewAction === 'approve' ? 'success' : 'danger'"
        :loading="reviewLoading"
        @click="submitReview"
      >
        {{ reviewAction === "approve" ? "Approve" : "Reject" }}
      </ElButton>
    </template>
  </ElDialog>
</template>

<style scoped>
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

.review-actions {
  display: inline-flex;
  align-items: center;
}

.review-btn {
  min-width: 72px;
  font-weight: 600;
}

.review-btn--approve {
  border-color: #67c23a;
}

.review-btn--reject {
  border-color: #f56c6c;
}

.review-btn--view {
  border-color: #909399;
}
</style>
