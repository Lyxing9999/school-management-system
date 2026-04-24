<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  ElButton,
  ElCard,
  ElCol,
  ElDatePicker,
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElEmpty,
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
  AttendanceDTO,
  AttendanceListParams,
  AttendanceStatus,
} from "~/api/hr_admin/attendance";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const attendanceService = hrmsAdminService().attendance;

const loading = ref(false);
const rows = ref<AttendanceDTO[]>([]);

const detailDialogVisible = ref(false);
const activeRow = ref<AttendanceDTO | null>(null);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  status: AttendanceStatus | "";
  start_date: string;
  end_date: string;
}>({
  status: "",
  start_date: "",
  end_date: "",
});

const statusSummary = computed(() => {
  const map = rows.value.reduce<Record<string, number>>((acc, row) => {
    const key = String(row.status || "unknown").toLowerCase();
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  return {
    checked_in: map.checked_in || 0,
    checked_out: map.checked_out || 0,
    late: map.late || 0,
    absent: map.absent || 0,
  };
});

const statCards = computed(() => [
  {
    label: "Total Records",
    value: pagination.total,
    hint: "Total rows from attendance history",
  },
  {
    label: "Checked Out",
    value: statusSummary.value.checked_out,
    hint: "Attendance days completed",
  },
  {
    label: "Late",
    value: statusSummary.value.late,
    hint: "Days with late check-in",
  },
  {
    label: "Absent",
    value: statusSummary.value.absent,
    hint: "Days marked absent",
  },
]);

const hasFilters = computed(() =>
  Boolean(filters.status || filters.start_date || filters.end_date),
);

const paginationProps = computed(() => ({
  currentPage: pagination.page,
  pageSize: pagination.limit,
  total: pagination.total,
}));

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
): "success" | "warning" | "danger" | "info" {
  const key = String(status || "").toLowerCase();
  if (key === "checked_out" || key === "wrong_location_approved")
    return "success";
  if (
    key === "checked_in" ||
    key === "late" ||
    key === "wrong_location_pending"
  )
    return "warning";
  if (key === "absent" || key === "wrong_location_rejected") return "danger";
  return "info";
}

function statusLabel(status?: string | null): string {
  if (!status) return "-";

  const map: Record<string, string> = {
    checked_in: "Checked In",
    checked_out: "Checked Out",
    late: "Late",
    early_leave: "Early Leave",
    absent: "Absent",
    holiday_off: "Holiday Off",
    weekend_off: "Weekend Off",
    wrong_location_pending: "Wrong Location Pending",
    wrong_location_approved: "Wrong Location Approved",
    wrong_location_rejected: "Wrong Location Rejected",
  };

  return map[String(status).toLowerCase()] || String(status);
}

function dayTypeLabel(dayType?: string | null): string {
  const map: Record<string, string> = {
    working_day: "Working Day",
    weekend: "Weekend",
    public_holiday: "Public Holiday",
  };

  return map[String(dayType || "").toLowerCase()] || "-";
}

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): AttendanceListParams {
  return {
    page,
    limit,
    status: filters.status || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
}

async function fetchHistory(page = pagination.page, limit = pagination.limit) {
  loading.value = true;

  try {
    const response = await attendanceService.getMyAttendance(
      buildParams(page, limit),
    );

    rows.value = response.items ?? [];

    const paginationRes = response.pagination;
    pagination.total = paginationRes?.total ?? rows.value.length;
    pagination.page = paginationRes?.page ?? page;
    pagination.limit = paginationRes?.page_size ?? limit;
  } catch {
    ElMessage.error("Failed to load attendance history");
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  pagination.page = 1;
  void fetchHistory(1, pagination.limit);
}

function resetFilters() {
  filters.status = "";
  filters.start_date = "";
  filters.end_date = "";
  pagination.page = 1;
  void fetchHistory(1, pagination.limit);
}

async function handlePageChange(page: number) {
  pagination.page = page;
  await fetchHistory(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchHistory(1, size);
}

function openDetail(row: AttendanceDTO) {
  activeRow.value = row;
  detailDialogVisible.value = true;
}

function closeDetail() {
  detailDialogVisible.value = false;
  activeRow.value = null;
}

function refreshList() {
  void fetchHistory(pagination.page, pagination.limit);
}

onMounted(() => {
  void fetchHistory(1, pagination.limit);
});
</script>

<template>
  <div class="attendance-history-page">
    <OverviewHeader
      title="Attendance History"
      description="My attendance records from /api/hrms/attendance/me"
      :backPath="ROUTES.EMPLOYEE.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="refreshList">
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="summary-row">
      <el-col
        v-for="item in statCards"
        :key="item.label"
        :xs="24"
        :sm="12"
        :lg="6"
      >
        <el-card class="summary-card" shadow="never" v-loading="loading">
          <p class="summary-card__label">{{ item.label }}</p>
          <p class="summary-card__value">{{ item.value }}</p>
          <p class="summary-card__hint">{{ item.hint }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="history-card" shadow="never">
      <template #header>
        <div class="history-card__header">
          <div>
            <h2 class="history-card__title">History Table</h2>
            <p class="history-card__subtitle">
              Filter by status and date range, then browse paginated records.
            </p>
          </div>

          <span class="history-card__count">{{ pagination.total }} total</span>
        </div>
      </template>

      <el-row :gutter="12" class="filter-grid">
        <el-col :xs="24" :md="8">
          <ElSelect
            v-model="filters.status"
            clearable
            class="w-full"
            placeholder="Status"
          >
            <ElOption label="Checked In" value="checked_in" />
            <ElOption label="Checked Out" value="checked_out" />
            <ElOption label="Late" value="late" />
            <ElOption label="Early Leave" value="early_leave" />
            <ElOption label="Absent" value="absent" />
            <ElOption
              label="Wrong Location Pending"
              value="wrong_location_pending"
            />
            <ElOption
              label="Wrong Location Approved"
              value="wrong_location_approved"
            />
            <ElOption
              label="Wrong Location Rejected"
              value="wrong_location_rejected"
            />
          </ElSelect>
        </el-col>

        <el-col :xs="24" :md="8">
          <ElDatePicker
            v-model="filters.start_date"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="Start date"
            class="w-full"
          />
        </el-col>

        <el-col :xs="24" :md="8">
          <ElDatePicker
            v-model="filters.end_date"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="End date"
            class="w-full"
          />
        </el-col>
      </el-row>

      <div class="filter-actions">
        <BaseButton type="primary" :loading="loading" @click="applyFilters">
          Apply Filters
        </BaseButton>
        <BaseButton
          plain
          :disabled="loading || !hasFilters"
          @click="resetFilters"
        >
          Reset
        </BaseButton>
      </div>

      <div class="table-shell" v-loading="loading">
        <ElEmpty
          v-if="!loading && rows.length === 0"
          description="No attendance history found"
        />

        <ElTable v-else :data="rows" stripe class="history-table">
          <ElTableColumn label="Date" width="130">
            <template #default="{ row }">
              {{ formatDate(row.attendance_date) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Check In" min-width="170">
            <template #default="{ row }">
              {{ formatDateTime(row.check_in_time) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Check Out" min-width="170">
            <template #default="{ row }">
              {{ formatDateTime(row.check_out_time) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Day Type" width="150">
            <template #default="{ row }">
              {{ dayTypeLabel(row.day_type) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Late (min)" width="110" align="right">
            <template #default="{ row }">
              {{ row.late_minutes ?? 0 }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Early Leave (min)" width="140" align="right">
            <template #default="{ row }">
              {{ row.early_leave_minutes ?? 0 }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Status" width="190">
            <template #default="{ row }">
              <ElTag :type="statusTagType(row.status)" effect="plain" round>
                {{ statusLabel(row.status) }}
              </ElTag>
            </template>
          </ElTableColumn>

          <ElTableColumn
            label="Actions"
            width="100"
            fixed="right"
            align="center"
          >
            <template #default="{ row }">
              <ElButton
                link
                type="primary"
                size="small"
                @click="openDetail(row)"
              >
                View
              </ElButton>
            </template>
          </ElTableColumn>
        </ElTable>
      </div>

      <div v-if="pagination.total > 0" class="pagination-row">
        <ElPagination
          :current-page="paginationProps.currentPage"
          :page-size="paginationProps.pageSize"
          :total="paginationProps.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <ElDialog
      v-model="detailDialogVisible"
      title="Attendance Detail"
      width="780px"
      @close="closeDetail"
    >
      <template v-if="activeRow">
        <ElDescriptions :column="2" border>
          <ElDescriptionsItem label="Employee">
            {{ displayRelation(activeRow.employee_name, activeRow.employee_id) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Date">
            {{ formatDate(activeRow.attendance_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Status">
            {{ statusLabel(activeRow.status) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Check In Time">
            {{ formatDateTime(activeRow.check_in_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Check Out Time">
            {{ formatDateTime(activeRow.check_out_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Day Type">
            {{ dayTypeLabel(activeRow.day_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="OT Eligible">
            {{ activeRow.is_ot_eligible ? "Yes" : "No" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Late Minutes">
            {{ activeRow.late_minutes ?? 0 }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Early Leave Minutes">
            {{ activeRow.early_leave_minutes ?? 0 }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Check-In Latitude">
            {{ activeRow.check_in_latitude ?? "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Check-In Longitude">
            {{ activeRow.check_in_longitude ?? "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Check-Out Latitude">
            {{ activeRow.check_out_latitude ?? "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Check-Out Longitude">
            {{ activeRow.check_out_longitude ?? "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Notes" :span="2">
            {{ activeRow.notes || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Wrong Location Reason" :span="2">
            {{ activeRow.wrong_location_reason || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Late Reason" :span="2">
            {{ activeRow.late_reason || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Early Leave Reason" :span="2">
            {{ activeRow.early_leave_reason || "-" }}
          </ElDescriptionsItem>
        </ElDescriptions>
      </template>

      <template #footer>
        <ElButton @click="closeDetail">Close</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.attendance-history-page {
  padding: 20px;
  max-width: 1520px;
  margin: 0 auto;
}

.summary-row {
  margin-bottom: 16px;
}

.summary-card {
  border-radius: 16px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, white 18%);
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}

.summary-card__label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #7a7f89;
}

.summary-card__value {
  margin: 8px 0 4px;
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--color-dark);
}

.summary-card__hint {
  margin: 0;
  font-size: 12px;
  color: #8a8f98;
}

.history-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, white 18%);
  box-shadow: 0 14px 36px rgba(16, 24, 40, 0.06);
}

.history-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.history-card__title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-dark);
}

.history-card__subtitle {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.history-card__count {
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

.history-table {
  width: 100%;
}

.pagination-row {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .history-card__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination-row {
    justify-content: flex-start;
  }
}
</style>
