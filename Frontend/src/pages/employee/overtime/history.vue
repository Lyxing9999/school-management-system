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
  OvertimeRequestDTO,
  OvertimeRequestListParams,
  OvertimeRequestStatus,
} from "~/api/hr_admin/overtime/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const overtimeService = hrmsAdminService().overtimeRequest;
const router = useRouter();

const loading = ref(false);
const rows = ref<OvertimeRequestDTO[]>([]);

const detailDialogVisible = ref(false);
const activeRow = ref<OvertimeRequestDTO | null>(null);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  status: OvertimeRequestStatus | "";
  start_date: string;
  end_date: string;
}>({
  status: "",
  start_date: "",
  end_date: "",
});

const hasFilters = computed(() =>
  Boolean(filters.status || filters.start_date || filters.end_date),
);

const summary = computed(() => {
  const map = rows.value.reduce<Record<string, number>>((acc, row) => {
    const key = String(row.status || "unknown").toLowerCase();
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  return [
    {
      label: "Total Records",
      value: pagination.total,
      hint: "Total overtime requests in history",
    },
    {
      label: "Pending",
      value: map.pending || 0,
      hint: "Requests waiting for review",
    },
    {
      label: "Approved",
      value: map.approved || 0,
      hint: "Approved overtime requests",
    },
    {
      label: "Rejected",
      value: map.rejected || 0,
      hint: "Rejected overtime requests",
    },
  ];
});

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

function formatTime(value?: string | null): string {
  if (!value) return "-";

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
  if (!Number.isFinite(amount)) return "-";

  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
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

function dayTypeLabel(dayType?: string | null): string {
  const map: Record<string, string> = {
    working_day: "Working Day",
    weekend: "Weekend",
    public_holiday: "Public Holiday",
  };

  return map[String(dayType || "").toLowerCase()] || "Unknown";
}

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): OvertimeRequestListParams {
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
    const response = await overtimeService.getMyRequests(
      buildParams(page, limit),
    );

    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.limit ?? limit;
  } catch {
    ElMessage.error("Failed to load overtime history");
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

function openDetail(row: OvertimeRequestDTO) {
  activeRow.value = row;
  detailDialogVisible.value = true;
}

function closeDetail() {
  detailDialogVisible.value = false;
  activeRow.value = null;
}

function refreshHistory() {
  void fetchHistory(pagination.page, pagination.limit);
}

onMounted(() => {
  void fetchHistory(1, pagination.limit);
});
</script>

<template>
  <div class="employee-overtime-history-page">
    <OverviewHeader
      title="Overtime History"
      description="My overtime requests from /api/hrms/overtime-requests/my"
      :backPath="ROUTES.EMPLOYEE.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="refreshHistory">
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loading"
          @click="router.push(ROUTES.EMPLOYEE.OVERTIME_REQUEST)"
        >
          Request Overtime
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="summary-row">
      <el-col
        v-for="item in summary"
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
            <h2 class="history-card__title">My Requests</h2>
            <p class="history-card__subtitle">
              Filter by status and period to review your overtime history.
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
            <ElOption label="Pending" value="pending" />
            <ElOption label="Approved" value="approved" />
            <ElOption label="Rejected" value="rejected" />
            <ElOption label="Cancelled" value="cancelled" />
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
          description="No overtime requests found"
        />

        <ElTable v-else :data="rows" stripe class="history-table">
          <ElTableColumn label="Request Date" min-width="130">
            <template #default="{ row }">
              {{ formatDate(row.request_date) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Time Range" min-width="170">
            <template #default="{ row }">
              {{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Hours" width="110" align="right">
            <template #default="{ row }">
              {{ estimateHours(row).toFixed(2) }}h
            </template>
          </ElTableColumn>

          <ElTableColumn label="Day Type" min-width="150">
            <template #default="{ row }">
              <ElTag effect="plain" round size="small">
                {{ dayTypeLabel(row.day_type) }}
              </ElTag>
            </template>
          </ElTableColumn>

          <ElTableColumn label="Reason" min-width="260">
            <template #default="{ row }">
              {{ row.reason }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Status" width="130">
            <template #default="{ row }">
              <ElTag
                :type="statusTagType(row.status)"
                effect="plain"
                round
                size="small"
              >
                {{
                  String(row.status || "-")
                    .charAt(0)
                    .toUpperCase() + String(row.status || "-").slice(1)
                }}
              </ElTag>
            </template>
          </ElTableColumn>

          <ElTableColumn label="Manager Comment" min-width="220">
            <template #default="{ row }">
              {{ row.manager_comment || "-" }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Submitted" min-width="170">
            <template #default="{ row }">
              {{ formatDateTime(row.submitted_at) }}
            </template>
          </ElTableColumn>

          <ElTableColumn
            label="Actions"
            width="100"
            align="center"
            fixed="right"
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
      title="Overtime Request Detail"
      width="760px"
      @close="closeDetail"
    >
      <template v-if="activeRow">
        <ElDescriptions :column="2" border>
          <ElDescriptionsItem label="Request ID">
            {{ activeRow.id }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Request Date">
            {{ formatDate(activeRow.request_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Start Time">
            {{ formatDateTime(activeRow.start_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="End Time">
            {{ formatDateTime(activeRow.end_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Schedule End Time">
            {{ formatDateTime(activeRow.schedule_end_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Submitted At">
            {{ formatDateTime(activeRow.submitted_at) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Status">
            {{ String(activeRow.status || "-").toUpperCase() }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Day Type">
            {{ dayTypeLabel(activeRow.day_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Approved Hours">
            {{ Number(activeRow.approved_hours || 0).toFixed(2) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Calculated Payment">
            {{ formatMoney(activeRow.calculated_payment) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Basic Salary">
            {{ formatMoney(activeRow.basic_salary) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager">
            {{
              displayRelation(
                activeRow.manager_name,
                activeRow.manager_user_id || activeRow.manager_id,
              )
            }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Reason" :span="2">
            {{ activeRow.reason }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager Comment" :span="2">
            {{ activeRow.manager_comment || "-" }}
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
.employee-overtime-history-page {
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
