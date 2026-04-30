<script setup lang="ts">
import { ref, onMounted, watch, reactive } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import {
  ElPagination,
  ElSelect,
  ElOption,
  ElDatePicker,
  ElTabs,
  ElTabPane,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElButton,
  ElTag,
  ElSpace,
} from "element-plus";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeAvatarCell from "~/components/table-edit/cells/EmployeeAvatarCell.vue";
import InlineStatusCell from "~/components/table-edit/cells/InlineStatusCell.vue";
import WorkLocationSelect from "~/components/selects/hr/WorkLocationSelect.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  AttendanceDTO,
  AttendanceTeamListParams,
  WrongLocationReportParams,
} from "~/api/hr_admin/attendance/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import type { ColumnConfig } from "~/components/types/tableEdit";

type ReviewAction = "approve" | "reject";

const hrms = hrmsAdminService();

// Team Attendance State
const loadingTeam = ref(false);
const hasFetchedTeam = ref(false);
const teamAttendances = ref<AttendanceDTO[]>([]);
const teamTotal = ref(0);
const teamPage = ref(1);
const teamPageSize = ref(10);
const teamStatus = ref<string | undefined>(undefined);
const teamDateRange = ref<[string, string] | null>(null);

// Wrong Location State
const loadingWrong = ref(false);
const hasFetchedWrong = ref(false);
const wrongLocationReports = ref<AttendanceDTO[]>([]);
const wrongTotal = ref(0);
const wrongPage = ref(1);
const wrongPageSize = ref(10);
const wrongReviewStatus = ref<string | undefined>(undefined);
const wrongDateRange = ref<[string, string] | null>(null);

// Wrong Location Review Dialog State
const reviewDialogVisible = ref(false);
const reviewAction = ref<ReviewAction>("approve");
const reviewLoading = ref(false);
const activeWrongLocationRow = ref<AttendanceDTO | null>(null);
const reviewFormRef = ref<FormInstance>();
const reviewForm = reactive({
  comment: "",
  location_id: null as string | null,
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

const statusOptions = [
  { label: "All", value: "" },
  { label: "Checked In", value: "checked_in" },
  { label: "Checked Out", value: "checked_out" },
  { label: "Late", value: "late" },
  { label: "Early Leave", value: "early_leave" },
  { label: "Absent", value: "absent" },
  { label: "Wrong Location Pending", value: "wrong_location_pending" },
  { label: "Wrong Location Approved", value: "wrong_location_approved" },
  { label: "Wrong Location Rejected", value: "wrong_location_rejected" },
];
const reviewStatusOptions = [
  { label: "All", value: "" },
  { label: "Pending", value: "pending" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
];

const fetchTeam = async () => {
  loadingTeam.value = true;
  try {
    const params: AttendanceTeamListParams = {
      page: teamPage.value,
      limit: teamPageSize.value,
      status: teamStatus.value || undefined,
      start_date: teamDateRange.value?.[0],
      end_date: teamDateRange.value?.[1],
    };
    const res = await hrms.attendance.getTeamAttendances(params);
    teamAttendances.value = res.items;
    teamTotal.value = res.pagination.total;
    hasFetchedTeam.value = true;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loadingTeam.value = false;
  }
};

const fetchWrong = async () => {
  loadingWrong.value = true;
  try {
    const params: WrongLocationReportParams = {
      page: wrongPage.value,
      limit: wrongPageSize.value,
      review_status: wrongReviewStatus.value || undefined,
      start_date: wrongDateRange.value?.[0],
      end_date: wrongDateRange.value?.[1],
    };
    const res = await hrms.attendance.getWrongLocationReports(params);
    wrongLocationReports.value = res.items;
    wrongTotal.value = res.pagination.total;
    hasFetchedWrong.value = true;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loadingWrong.value = false;
  }
};

onMounted(() => {
  fetchTeam();
  fetchWrong();
});

watch([teamPage, teamPageSize, teamStatus, teamDateRange], fetchTeam);
watch(
  [wrongPage, wrongPageSize, wrongReviewStatus, wrongDateRange],
  fetchWrong,
);

const columns: ColumnConfig<AttendanceDTO>[] = [
  {
    label: "Employee",
    field: "employee_id",
    minWidth: 180,
    useSlot: true,
    slotName: "employee",
  },
  {
    label: "Date",
    field: "attendance_date",
    minWidth: 120,
  },
  {
    label: "Check In",
    field: "check_in_time",
    minWidth: 120,
  },
  {
    label: "Check Out",
    field: "check_out_time",
    minWidth: 120,
  },
  {
    label: "Status",
    field: "status",
    minWidth: 140,
    useSlot: true,
    slotName: "status",
  },
  {
    label: "Late (min)",
    field: "late_minutes",
    minWidth: 100,
  },
  {
    label: "Early Leave (min)",
    field: "early_leave_minutes",
    minWidth: 120,
  },
];

const wrongColumns: ColumnConfig<AttendanceDTO>[] = [
  {
    label: "Employee",
    field: "employee_id",
    minWidth: 180,
    useSlot: true,
    slotName: "employee",
  },
  {
    label: "Date",
    field: "attendance_date",
    minWidth: 120,
  },
  {
    label: "Check In",
    field: "check_in_time",
    minWidth: 120,
  },
  {
    label: "Wrong Location Reason",
    field: "wrong_location_reason",
    minWidth: 180,
  },
  {
    label: "Assigned Location",
    field: "location_name",
    minWidth: 180,
    render: (row: AttendanceDTO) =>
      displayRelation(row.location_name, row.location_id),
  },
  {
    label: "Review Status",
    field: "location_review_status",
    minWidth: 140,
    useSlot: true,
    slotName: "review_status",
  },
  {
    label: "Reviewed By",
    field: "location_reviewed_by_name",
    minWidth: 160,
    render: (row: AttendanceDTO) =>
      displayRelation(row.location_reviewed_by_name, row.location_reviewed_by),
  },
  {
    label: "Admin Comment",
    field: "admin_comment",
    minWidth: 160,
  },
  {
    label: "Actions",
    field: "id",
    minWidth: 210,
    useSlot: true,
    slotName: "operation",
  },
];

function resolvedStatus(row: AttendanceDTO): string {
  const wrongLocationStatus = String(row.wrong_location_status || "")
    .trim()
    .toLowerCase();
  if (wrongLocationStatus) return wrongLocationStatus;

  const reviewStatus = String(row.location_review_status || "")
    .trim()
    .toLowerCase();
  if (reviewStatus === "pending") return "wrong_location_pending";
  if (reviewStatus === "approved") return "wrong_location_approved";
  if (reviewStatus === "rejected") return "wrong_location_rejected";

  return String(row.status || "").toLowerCase();
}

function reviewStatusLabel(row: AttendanceDTO): string {
  const status = resolvedStatus(row);
  if (status === "wrong_location_pending") return "Pending";
  if (status === "wrong_location_approved") return "Approved";
  if (status === "wrong_location_rejected") return "Rejected";
  return "-";
}

function reviewStatusType(
  row: AttendanceDTO,
): "warning" | "success" | "danger" | "info" {
  const status = resolvedStatus(row);
  if (status === "wrong_location_pending") return "warning";
  if (status === "wrong_location_approved") return "success";
  if (status === "wrong_location_rejected") return "danger";
  return "info";
}

function isPendingWrongLocation(row: AttendanceDTO): boolean {
  return resolvedStatus(row) === "wrong_location_pending";
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

function mapError(error: unknown, fallback: string): string {
  if (error && typeof error === "object" && "response" in error) {
    const e = error as {
      response?: { data?: { user_message?: string; message?: string } };
    };
    return e.response?.data?.user_message || e.response?.data?.message || fallback;
  }

  if (error instanceof Error && error.message) return error.message;
  return fallback;
}

function openWrongLocationReviewDialog(row: AttendanceDTO, action: ReviewAction) {
  if (!isPendingWrongLocation(row)) {
    ElMessageBox.alert(
      "Only pending wrong-location cases can be reviewed",
      "Cannot Review",
      { type: "warning" },
    );
    return;
  }

  activeWrongLocationRow.value = row;
  reviewAction.value = action;
  reviewForm.comment = "";
  reviewForm.location_id = action === "approve" ? row.location_id || null : null;
  reviewDialogVisible.value = true;
}

async function submitWrongLocationReview() {
  if (!activeWrongLocationRow.value) return;

  await reviewFormRef.value?.validate();

  reviewLoading.value = true;
  try {
    await hrms.attendance.reviewWrongLocation(
      activeWrongLocationRow.value.id,
      {
        approved: reviewAction.value === "approve",
        comment: reviewForm.comment.trim() || null,
        location_id:
          reviewAction.value === "approve"
            ? reviewForm.location_id || null
            : null,
      },
      { showSuccess: false, showError: false },
    );

    ElMessage.success(
      reviewAction.value === "approve"
        ? "Wrong-location case approved"
        : "Wrong-location case rejected",
    );

    reviewDialogVisible.value = false;
    activeWrongLocationRow.value = null;
    await fetchWrong();
  } catch (error) {
    ElMessage.error(mapError(error, "Failed to submit review action"));
  } finally {
    reviewLoading.value = false;
  }
}

async function showWrongLocationDetails(row: AttendanceDTO) {
  await ElMessageBox.alert(
    `Employee: ${displayRelation(
      row.employee_name,
      row.employee_id,
    )}\nAttendance Date: ${formatDate(
      row.attendance_date,
    )}\nCheck In: ${formatDateTime(row.check_in_time)}\nReview Status: ${reviewStatusLabel(
      row,
    )}\nAssigned location: ${
      displayRelation(row.location_name, row.location_id) || "-"
    }\nReviewed by: ${
      displayRelation(row.location_reviewed_by_name, row.location_reviewed_by) ||
      "-"
    }\nWrong-location reason: ${row.wrong_location_reason || "-"}\nReviewer comment: ${
      row.admin_comment || "-"
    }`,
    "Wrong-location details",
    { type: "info" },
  );
}
</script>

<template>
  <ElTabs type="border-card">
    <ElTabPane label="Team Attendance">
      <TableCard
        title="Team Attendance"
        description="View and filter your team's attendance records."
      >
        <template #header-right>
          <ElSelect
            v-model="teamStatus"
            placeholder="Status"
            style="width: 160px; margin-right: 12px"
          >
            <ElOption
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </ElSelect>
          <ElDatePicker
            v-model="teamDateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start date"
            end-placeholder="End date"
            style="width: 260px"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
          />
        </template>
        <SmartTable
          :data="teamAttendances"
          :columns="columns"
          :loading="loadingTeam"
          :hasFetchedOnce="hasFetchedTeam"
          :smartProps="{ border: true, stripe: true }"
        >
          <template #employee="{ row }">
            <EmployeeAvatarCell :row="row" />
            <span style="margin-left: 8px">{{
              displayRelation(row.employee_name || row.full_name, row.employee_id)
            }}</span>
          </template>
          <template #status="{ row }">
            <InlineStatusCell
              :row-id="row.id"
              :value="resolvedStatus(row as AttendanceDTO)"
              :editing-row-id="null"
              :draft="resolvedStatus(row as AttendanceDTO)"
              :options="statusOptions.filter((o) => o.value)"
              :tag-type="
                (v) => {
                  switch (v) {
                    case 'checked_in':
                      return 'info';
                    case 'checked_out':
                      return 'success';
                    case 'late':
                      return 'warning';
                    case 'early_leave':
                      return 'warning';
                    case 'absent':
                      return 'danger';
                    case 'wrong_location_pending':
                      return 'warning';
                    case 'wrong_location_approved':
                      return 'success';
                    case 'wrong_location_rejected':
                      return 'danger';
                    default:
                      return '';
                  }
                }
              "
              :format-label="
                (v) =>
                  statusOptions.find((o) => o.value === String(v))?.label ||
                  String(v ?? '')
              "
              disabled
            />
          </template>
        </SmartTable>
        <div style="margin-top: 16px; text-align: right">
          <ElPagination
            v-model:current-page="teamPage"
            v-model:page-size="teamPageSize"
            :total="teamTotal"
            :page-sizes="[10, 20, 50]"
            layout="prev, pager, next, sizes"
            background
            small
          />
        </div>
      </TableCard>
    </ElTabPane>
    <ElTabPane label="Wrong Location Reports">
      <TableCard
        title="Wrong Location Reports"
        description="Attendance records flagged for wrong location."
      >
        <template #header-right>
          <ElSelect
            v-model="wrongReviewStatus"
            placeholder="Review Status"
            style="width: 140px; margin-right: 8px"
          >
            <ElOption
              v-for="opt in reviewStatusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </ElSelect>
          <ElDatePicker
            v-model="wrongDateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start date"
            end-placeholder="End date"
            style="width: 260px"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            clearable
          />
        </template>
        <SmartTable
          :data="wrongLocationReports"
          :columns="wrongColumns"
          :loading="loadingWrong"
          :hasFetchedOnce="hasFetchedWrong"
          :smartProps="{ border: true, stripe: true }"
        >
          <template #employee="{ row }">
            <EmployeeAvatarCell :row="row" />
            <span style="margin-left: 8px">{{
              displayRelation(row.employee_name || row.full_name, row.employee_id)
            }}</span>
          </template>
          <template #review_status="{ row }">
            <ElTag
              :type="reviewStatusType(row as AttendanceDTO)"
              effect="plain"
              round
              size="small"
            >
              {{ reviewStatusLabel(row as AttendanceDTO) }}
            </ElTag>
          </template>
          <template #operation="{ row }">
            <ElSpace class="review-actions" :size="6">
              <template v-if="isPendingWrongLocation(row as AttendanceDTO)">
                <ElButton
                  type="success"
                  size="small"
                  plain
                  class="review-btn review-btn--approve"
                  @click.stop="
                    openWrongLocationReviewDialog(row as AttendanceDTO, 'approve')
                  "
                >
                  Approve
                </ElButton>
                <ElButton
                  type="danger"
                  size="small"
                  plain
                  class="review-btn review-btn--reject"
                  @click.stop="
                    openWrongLocationReviewDialog(row as AttendanceDTO, 'reject')
                  "
                >
                  Reject
                </ElButton>
              </template>
              <ElButton
                type="info"
                size="small"
                plain
                class="review-btn review-btn--view"
                @click.stop="showWrongLocationDetails(row as AttendanceDTO)"
              >
                View
              </ElButton>
            </ElSpace>
          </template>
        </SmartTable>
        <div style="margin-top: 16px; text-align: right">
          <ElPagination
            v-model:current-page="wrongPage"
            v-model:page-size="wrongPageSize"
            :total="wrongTotal"
            :page-sizes="[10, 20, 50]"
            layout="prev, pager, next, sizes"
            background
            small
          />
        </div>
      </TableCard>
    </ElTabPane>
  </ElTabs>

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
            displayRelation(
              activeWrongLocationRow?.employee_name,
              activeWrongLocationRow?.employee_id,
            )
          "
          readonly
        />
      </ElFormItem>
      <ElFormItem label="Date">
        <ElInput
          :model-value="formatDate(activeWrongLocationRow?.attendance_date)"
          readonly
        />
      </ElFormItem>
      <ElFormItem label="Reason">
        <ElInput
          :model-value="activeWrongLocationRow?.wrong_location_reason || '-'"
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
        @click="submitWrongLocationReview"
      >
        {{ reviewAction === "approve" ? "Approve" : "Reject" }}
      </ElButton>
    </template>
  </ElDialog>
</template>

<style scoped>
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
