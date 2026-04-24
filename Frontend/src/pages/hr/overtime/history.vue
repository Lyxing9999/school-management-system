<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import type { FormInstance } from "element-plus";
import {
  ElButton,
  ElCard,
  ElCol,
  ElDatePicker,
  ElDescriptions,
  ElDescriptionsItem,
  ElDialog,
  ElEmpty,
  ElInput,
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

const router = useRouter();
const overtimeService = hrmsAdminService().overtimeRequest;

const loading = ref(false);
const rows = ref<OvertimeRequestDTO[]>([]);
const detailDialogVisible = ref(false);
const activeRequest = ref<OvertimeRequestDTO | null>(null);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  employee_id: string;
  status: OvertimeRequestStatus | undefined;
  start_date: string;
  end_date: string;
}>({
  employee_id: "",
  status: undefined,
  start_date: "",
  end_date: "",
});

const activeFilterBadge = computed(() => {
  return [
    Boolean(filters.employee_id.trim()),
    Boolean(filters.status),
    Boolean(filters.start_date),
    Boolean(filters.end_date),
  ].filter(Boolean).length;
});

const statusSummary = computed(() => {
  const counts = rows.value.reduce((acc, row) => {
    const key = String(row.status || "unknown").toLowerCase();
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return [
    { label: "Pending", value: counts.pending || 0 },
    { label: "Approved", value: counts.approved || 0 },
    { label: "Rejected", value: counts.rejected || 0 },
    { label: "Cancelled", value: counts.cancelled || 0 },
  ];
});

const paginationProps = computed(() => ({
  currentPage: pagination.page,
  pageSize: pagination.limit,
  total: pagination.total,
}));

function buildParams(
  page = pagination.page,
  limit = pagination.limit,
): OvertimeRequestListParams {
  return {
    page,
    limit,
    employee_id: filters.employee_id.trim() || undefined,
    status: filters.status,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
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

function openDetails(row: OvertimeRequestDTO) {
  activeRequest.value = row;
  detailDialogVisible.value = true;
}

function closeDetails() {
  detailDialogVisible.value = false;
  activeRequest.value = null;
}

async function fetchOvertimeRequests(
  page = pagination.page,
  limit = pagination.limit,
) {
  loading.value = true;
  try {
    const response = await overtimeService.getRequests(
      buildParams(page, limit),
    );
    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.limit ?? limit;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchOvertimeRequests(1, pagination.limit);
}

function resetFilters() {
  filters.employee_id = "";
  filters.status = undefined;
  filters.start_date = "";
  filters.end_date = "";
  void applyFilters();
}

async function handlePageChange(page: number) {
  pagination.page = page;
  await fetchOvertimeRequests(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchOvertimeRequests(1, size);
}

async function refreshHistory() {
  await fetchOvertimeRequests(pagination.page, pagination.limit);
}

import { onMounted } from "vue";
onMounted(() => {
  fetchOvertimeRequests(1, pagination.limit);
});
</script>

<template>
  <div class="overtime-history-page">
    <OverviewHeader
      title="Overtime History"
      description="Review overtime requests across employees with search and date filters"
    >
      <template #actions>
        <BaseButton
          plain
          :loading="loading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="refreshHistory"
        >
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loading"
          @click="router.push(ROUTES.HR_ADMIN.OVERTIME)"
        >
          Back
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="12" class="summary-row">
      <el-col v-for="item in statusSummary" :key="item.label" :xs="12" :sm="6">
        <el-card class="summary-card" shadow="never">
          <p class="summary-card__label">{{ item.label }}</p>
          <p class="summary-card__value">{{ item.value }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="history-card" shadow="never">
      <template #header>
        <div class="history-card__header">
          <div>
            <h2 class="history-card__title">All Overtime Requests</h2>
            <p class="history-card__subtitle">
              Use the filters below to narrow the history list.
            </p>
          </div>
          <span class="history-card__count">{{ pagination.total }} total</span>
        </div>
      </template>

      <el-row :gutter="12" class="filter-grid">
        <el-col :xs="24" :md="8">
          <ElInput
            v-model="filters.employee_id"
            clearable
            placeholder="Filter by employee"
            @keyup.enter="applyFilters"
          />
        </el-col>

        <el-col :xs="24" :md="6">
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

        <el-col :xs="24" :md="5">
          <ElDatePicker
            v-model="filters.start_date"
            class="w-full"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="Start date"
          />
        </el-col>

        <el-col :xs="24" :md="5">
          <ElDatePicker
            v-model="filters.end_date"
            class="w-full"
            type="date"
            value-format="YYYY-MM-DD"
            format="YYYY-MM-DD"
            placeholder="End date"
          />
        </el-col>
      </el-row>

      <div class="filter-actions">
        <BaseButton type="primary" :loading="loading" @click="applyFilters">
          Apply Filters
          <span v-if="activeFilterBadge" class="filter-badge">{{
            activeFilterBadge
          }}</span>
        </BaseButton>
        <BaseButton plain :disabled="loading" @click="resetFilters"
          >Reset</BaseButton
        >
      </div>

      <div class="table-shell" v-loading="loading">
        <el-empty
          v-if="!loading && rows.length === 0"
          description="No overtime requests found"
        />

        <ElTable v-else :data="rows" stripe class="history-table">
          <ElTableColumn label="Employee" min-width="160">
            <template #default="{ row }">
              <div class="employee-cell">
                <span class="employee-cell__primary">{{
                  displayRelation(row.employee_name, row.employee_id)
                }}</span>
              </div>
            </template>
          </ElTableColumn>

          <ElTableColumn label="Request Date" min-width="130">
            <template #default="{ row }">{{
              formatDate(row.request_date)
            }}</template>
          </ElTableColumn>

          <ElTableColumn label="Time Range" min-width="170">
            <template #default="{ row }">
              {{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Hours" width="100">
            <template #default="{ row }"
              >{{ estimateHours(row).toFixed(2) }}h</template
            >
          </ElTableColumn>

          <ElTableColumn label="Day Type" min-width="150">
            <template #default="{ row }">
              <ElTag effect="plain" round size="small" class="day-type-pill">
                {{ dayTypeLabel(row.day_type) }}
              </ElTag>
            </template>
          </ElTableColumn>

          <ElTableColumn label="Reason" min-width="260">
            <template #default="{ row }">
              <span class="reason-cell">{{ row.reason }}</span>
            </template>
          </ElTableColumn>

          <ElTableColumn label="Status" width="130">
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
          </ElTableColumn>

          <ElTableColumn label="Manager Comment" min-width="220">
            <template #default="{ row }">
              {{ row.manager_comment || "—" }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Submitted" min-width="170">
            <template #default="{ row }">{{
              formatDateTime(row.submitted_at)
            }}</template>
          </ElTableColumn>

          <ElTableColumn
            label="Actions"
            width="120"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <ElButton
                link
                type="primary"
                size="small"
                @click="openDetails(row)"
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
      @close="closeDetails"
    >
      <template v-if="activeRequest">
        <div class="detail-head">
          <div>
            <h3 class="detail-head__title">
              {{ displayRelation(activeRequest.employee_name, activeRequest.employee_id) }}
            </h3>
          </div>

          <ElTag
            :type="statusTagType(activeRequest.status)"
            effect="plain"
            round
            size="small"
            :class="statusClass(activeRequest.status)"
          >
            {{
              String(activeRequest.status || "-")
                .charAt(0)
                .toUpperCase() + String(activeRequest.status || "-").slice(1)
            }}
          </ElTag>
        </div>

        <ElDescriptions :column="2" border class="mt-4">
          <ElDescriptionsItem label="Employee">
            {{
              displayRelation(activeRequest.employee_name, activeRequest.employee_id)
            }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Request Date">
            {{ formatDate(activeRequest.request_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Start Time">
            {{ formatDateTime(activeRequest.start_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="End Time">
            {{ formatDateTime(activeRequest.end_time) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Submitted At">
            {{ formatDateTime(activeRequest.submitted_at) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Day Type">
            {{ dayTypeLabel(activeRequest.day_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Approved Hours">
            {{ Number(activeRequest.approved_hours || 0).toFixed(2) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Calculated Payment">
            {{ formatMoney(activeRequest.calculated_payment) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Basic Salary">
            {{ formatMoney(activeRequest.basic_salary) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager">
            {{
              displayRelation(
                activeRequest.manager_name,
                activeRequest.manager_user_id || activeRequest.manager_id,
              )
            }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Reason" :span="2">
            {{ activeRequest.reason }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager Comment" :span="2">
            {{ activeRequest.manager_comment || "—" }}
          </ElDescriptionsItem>
        </ElDescriptions>
      </template>

      <template #footer>
        <ElButton @click="closeDetails">Close</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.overtime-history-page {
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
  margin: 8px 0 0;
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--color-dark);
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

.filter-badge {
  margin-left: 6px;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 11px;
  line-height: 18px;
  background: color-mix(in srgb, var(--color-primary) 20%, white 80%);
}

.table-shell {
  min-height: 220px;
}

.history-table {
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

@media (max-width: 768px) {
  .history-card__header,
  .detail-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination-row {
    justify-content: flex-start;
  }
}
</style>
