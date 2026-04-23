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
  ElSelect,
  ElTag,
} from "element-plus";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import WorkLocationSelect from "~/components/selects/hr/WorkLocationSelect.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type { AttendanceDTO } from "~/api/hr_admin/attendance";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import type { ColumnConfig } from "~/components/types/tableEdit";

definePageMeta({ layout: "default" });

type ReviewAction = "approve" | "reject";
type StatusFilter = "all" | "pending" | "approved" | "rejected";

const attendanceService = hrmsAdminService().attendance;
const workLocationService = hrmsAdminService().workLocation;

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
  location_id: null as string | null,
});

const workLocationOptions = ref<Array<{ value: string; label: string }>>([]);

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
  location_id: [
    {
      validator: (_rule, value: string | null, callback) => {
        if (reviewAction.value === "approve" && !String(value || "").trim()) {
          callback(new Error("Location is required when approving"));
          return;
        }
        callback();
      },
      trigger: "change",
    },
  ],
};

const tableColumns: ColumnConfig<AttendanceDTO>[] = [
  {
    field: "employee_id",
    label: "Employee",
    minWidth: "130px",
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
    field: "check_in_time",
    label: "Check In",
    width: "160px",
    visible: true,
    render: (row: AttendanceDTO) => formatDateTime(row.check_in_time),
  },
  {
    field: "wrong_location_reason",
    label: "Reason",
    minWidth: "220px",
    visible: true,
    render: (row: AttendanceDTO) => row.wrong_location_reason || "-",
  },
  {
    field: "location_id",
    label: "Assigned Location",
    minWidth: "180px",
    visible: true,
    render: (row: AttendanceDTO) =>
      displayRelation(row.location_name, getLocationLabel(row.location_id)),
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
    const statusKey = normalizeWrongLocationStatus(row.status);
    if (statusFilter.value !== "all" && statusKey !== statusFilter.value) {
      return false;
    }

    if (!keyword) return true;

    return (
      String(row.id || "")
        .toLowerCase()
        .includes(keyword) ||
      String(displayRelation(row.employee_name, row.employee_id))
        .toLowerCase()
        .includes(keyword) ||
      String(row.wrong_location_reason || "")
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

function normalizeWrongLocationStatus(status?: string | null): StatusFilter {
  const value = String(status || "").toLowerCase();
  if (value === "wrong_location_pending") return "pending";
  if (value === "wrong_location_approved") return "approved";
  if (value === "wrong_location_rejected") return "rejected";
  return "all";
}

function statusLabel(status?: string | null): string {
  const map: Record<string, string> = {
    wrong_location_pending: "Pending",
    wrong_location_approved: "Approved",
    wrong_location_rejected: "Rejected",
  };
  return map[String(status || "").toLowerCase()] || "Unknown";
}

function isPendingWrongLocation(status?: string | null): boolean {
  return String(status || "").toLowerCase() === "wrong_location_pending";
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
    wrong_location_pending: "warning",
    wrong_location_approved: "success",
    wrong_location_rejected: "danger",
  };
  return map[String(status || "").toLowerCase()] || "info";
}

function statusClass(status?: string | null): string {
  const map: Record<string, string> = {
    wrong_location_pending: "status-pill status-pill--pending",
    wrong_location_approved: "status-pill status-pill--approved",
    wrong_location_rejected: "status-pill status-pill--rejected",
  };
  return map[String(status || "").toLowerCase()] || "status-pill";
}

function getLocationLabel(locationId?: string | null): string {
  if (!locationId) return "-";
  const found = workLocationOptions.value.find(
    (opt) => opt.value === locationId,
  );
  return found?.label || locationId;
}

async function fetchWorkLocations() {
  try {
    workLocationOptions.value =
      await workLocationService.getWorkLocationSelectOptions({
        showError: false,
      });
  } catch {
    workLocationOptions.value = [];
  }
}

async function fetchWrongLocationReports(page = currentPage.value) {
  loading.value = true;

  try {
    const statusParam =
      statusFilter.value === "all"
        ? undefined
        : `wrong_location_${statusFilter.value}`;

    const response = await attendanceService.getWrongLocationReports({
      page,
      limit: pageSize.value,
      ...(statusParam ? { status: statusParam } : {}),
    } as any);

    rows.value = response.items ?? [];
    const pagination = response.pagination;

    totalRows.value = pagination?.total ?? rows.value.length;
    currentPage.value = pagination?.page ?? page;
    pageSize.value = pagination?.page_size ?? pageSize.value;
  } catch {
    ElMessage.error("Failed to load wrong-location reports");
  } finally {
    loading.value = false;
  }
}

function openReviewDialog(row: AttendanceDTO, action: ReviewAction) {
  if (!isPendingWrongLocation(row.status)) {
    ElMessageBox.alert(
      "Only pending wrong-location cases can be reviewed",
      "Cannot Review",
      { type: "warning" },
    );
    return;
  }

  activeRow.value = row;
  reviewAction.value = action;
  reviewForm.comment = "";
  reviewForm.location_id =
    action === "approve" ? row.location_id || null : null;
  reviewDialogVisible.value = true;
}

async function submitReview() {
  if (!activeRow.value) return;

  await reviewFormRef.value?.validate();

  reviewLoading.value = true;
  try {
    await attendanceService.reviewWrongLocation(activeRow.value.id, {
      approved: reviewAction.value === "approve",
      comment: reviewForm.comment.trim() || null,
      location_id:
        reviewAction.value === "approve"
          ? reviewForm.location_id || null
          : null,
    });

    ElMessage.success(
      reviewAction.value === "approve"
        ? "Wrong-location case approved"
        : "Wrong-location case rejected",
    );

    reviewDialogVisible.value = false;
    activeRow.value = null;
    await fetchWrongLocationReports(currentPage.value);
  } catch {
    ElMessage.error("Failed to submit review action");
  } finally {
    reviewLoading.value = false;
  }
}

async function showDetails(row: AttendanceDTO) {
  await ElMessageBox.alert(
    `Attendance ID: ${row.id}\nEmployee: ${
      displayRelation(row.employee_name, row.employee_id)
    }\nAttendance Date: ${formatDate(
      row.attendance_date,
    )}\nCheck In: ${formatDateTime(row.check_in_time)}\nStatus: ${statusLabel(
      row.status,
    )}\nAssigned location: ${displayRelation(
      row.location_name,
      getLocationLabel(row.location_id),
    )}\nWrong-location reason: ${
      row.wrong_location_reason || "-"
    }\nReviewer comment: ${row.admin_comment || "-"}`,
    "Wrong-location details",
    { type: "info" },
  );
}

const handleChangePageSize = async (size: number) => {
  pageSize.value = size;
  await fetchWrongLocationReports(1);
};

watch(statusFilter, async () => {
  await fetchWrongLocationReports(1);
});

onMounted(() => {
  Promise.all([fetchWorkLocations(), fetchWrongLocationReports(1)]);
});
</script>

<template>
  <OverviewHeader
    :title="'Wrong Location Reviews'"
    :description="'Review pending and completed wrong-location attendance cases'"
    :backPath="'/hr/attendance'"
  >
    <template #actions>
      <BaseButton
        plain
        :loading="loading"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="fetchWrongLocationReports(currentPage || 1)"
      >
        Refresh
      </BaseButton>
    </template>
  </OverviewHeader>

  <el-row :gutter="16" class="mb-4">
    <el-col :span="12">
      <el-input
        v-model="query"
        placeholder="Search ID, employee, reason"
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
    @page="fetchWrongLocationReports"
    @page-size="handleChangePageSize"
  >
    <template #status="{ row }">
      <el-tag
        :type="statusTagType(row.status)"
        effect="plain"
        round
        size="small"
        :class="statusClass(row.status)"
      >
        {{ statusLabel(row.status) }}
      </el-tag>
    </template>

    <template #operation="{ row }">
      <el-space class="review-actions" :size="6">
        <template v-if="isPendingWrongLocation(row.status)">
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
      @current-change="fetchWrongLocationReports"
      @size-change="handleChangePageSize"
    />
  </el-row>

  <ElDialog
    v-model="reviewDialogVisible"
    :title="
      reviewAction === 'approve'
        ? 'Approve Wrong-Location Case'
        : 'Reject Wrong-Location Case'
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
      <ElFormItem label="Reason">
        <ElInput
          :model-value="activeRow?.wrong_location_reason || '-'"
          type="textarea"
          readonly
          :rows="3"
        />
      </ElFormItem>
      <ElFormItem label="Location" prop="location_id">
        <WorkLocationSelect
          v-model="reviewForm.location_id"
          :clearable="reviewAction !== 'approve'"
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
