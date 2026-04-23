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
  LeaveRequestDTO,
  LeaveRequestListParams,
  LeaveRequestStatus,
} from "~/api/hr_admin/leave/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const router = useRouter();
const leaveService = hrmsAdminService().leaveRequest;

const loading = ref(false);
const rows = ref<LeaveRequestDTO[]>([]);
const detailDialogVisible = ref(false);
const activeRequest = ref<LeaveRequestDTO | null>(null);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  employee_id: string;
  status: LeaveRequestStatus | undefined;
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

const summaryStats = computed(() => {
  const counts = rows.value.reduce((acc, row) => {
    const key = String(row.status || "unknown").toLowerCase();
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return [
    { label: "Total", value: pagination.total },
    { label: "Pending", value: counts.pending || 0 },
    { label: "Approved", value: counts.approved || 0 },
    { label: "Rejected", value: counts.rejected || 0 },
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
): LeaveRequestListParams {
  return {
    page,
    limit,
    employee_id: filters.employee_id.trim() || undefined,
    status: filters.status,
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

function leaveTypeLabel(value?: string | null): string {
  if (!value) return "—";
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatMoney(value?: number | null): string {
  const amount = Number(value ?? 0);
  if (!Number.isFinite(amount)) return "—";

  return amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function openDetails(row: LeaveRequestDTO) {
  activeRequest.value = row;
  detailDialogVisible.value = true;
}

function closeDetails() {
  detailDialogVisible.value = false;
  activeRequest.value = null;
}

async function fetchLeaveRequests(
  page = pagination.page,
  limit = pagination.limit,
) {
  loading.value = true;
  try {
    const response = await leaveService.getRequests(buildParams(page, limit));
    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.page_size ?? limit;
  } catch {
    ElMessage.error("Failed to load leave requests");
  } finally {
    loading.value = false;
  }
}

async function applyFilters() {
  pagination.page = 1;
  await fetchLeaveRequests(1, pagination.limit);
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
  await fetchLeaveRequests(page, pagination.limit);
}

async function handlePageSizeChange(size: number) {
  pagination.limit = size;
  pagination.page = 1;
  await fetchLeaveRequests(1, size);
}

async function refreshList() {
  await fetchLeaveRequests(pagination.page, pagination.limit);
}

onMounted(() => {
  fetchLeaveRequests(1, pagination.limit);
});
</script>

<template>
  <div class="leave-overview-page">
    <OverviewHeader
      title="Leave Overview"
      description="All leave requests across employees"
    >
      <template #actions>
        <BaseButton
          plain
          :loading="loading"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="refreshList"
        >
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loading"
          @click="router.push(ROUTES.HR_ADMIN.DASHBOARD)"
        >
          Back
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="12" class="summary-row">
      <el-col v-for="item in summaryStats" :key="item.label" :xs="12" :sm="6">
        <el-card class="summary-card" shadow="never">
          <p class="summary-card__label">{{ item.label }}</p>
          <p class="summary-card__value">{{ item.value }}</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="leave-card" shadow="never">
      <template #header>
        <div class="leave-card__header">
          <div>
            <h2 class="leave-card__title">All Requests</h2>
            <p class="leave-card__subtitle">
              Filter by employee, status, and prepare for date range support
              later.
            </p>
          </div>

          <span class="leave-card__count">{{ pagination.total }} total</span>
        </div>
      </template>

      <el-row :gutter="12" class="filter-grid">
        <el-col :xs="24" :md="8">
          <ElInput
            v-model="filters.employee_id"
            clearable
            placeholder="Filter by employee id"
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
            disabled
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
            disabled
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
          description="No leave requests found"
        />

        <ElTable v-else :data="rows" stripe class="leave-table">
          <ElTableColumn label="Employee" min-width="160">
            <template #default="{ row }">
              <div class="employee-cell">
                <span class="employee-cell__primary">{{
                  displayRelation(row.employee_name, row.employee_id)
                }}</span>
                <span class="employee-cell__secondary">{{ row.id }}</span>
              </div>
            </template>
          </ElTableColumn>

          <ElTableColumn label="Leave Type" min-width="150">
            <template #default="{ row }">
              {{ leaveTypeLabel(row.leave_type) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Start Date" min-width="130">
            <template #default="{ row }">{{
              formatDate(row.start_date)
            }}</template>
          </ElTableColumn>

          <ElTableColumn label="End Date" min-width="130">
            <template #default="{ row }">{{
              formatDate(row.end_date)
            }}</template>
          </ElTableColumn>

          <ElTableColumn label="Days" width="90">
            <template #default="{ row }">{{
              Number(row.total_days || 0).toFixed(1)
            }}</template>
          </ElTableColumn>

          <ElTableColumn label="Paid" width="90">
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
      title="Leave Request Detail"
      width="760px"
      @close="closeDetails"
    >
      <template v-if="activeRequest">
        <div class="detail-head">
          <div>
            <h3 class="detail-head__title">
              {{ displayRelation(activeRequest.employee_name, activeRequest.employee_id) }}
            </h3>
            <p class="detail-head__subtitle">Request {{ activeRequest.id }}</p>
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
          <ElDescriptionsItem label="Leave Type">
            {{ leaveTypeLabel(activeRequest.leave_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Start Date">
            {{ formatDate(activeRequest.start_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="End Date">
            {{ formatDate(activeRequest.end_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Total Days">
            {{ Number(activeRequest.total_days || 0).toFixed(1) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Paid Leave">
            {{ activeRequest.is_paid ? "Yes" : "No" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager">
            {{
              displayRelation(activeRequest.manager_name, activeRequest.manager_user_id)
            }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Contract Start">
            {{ formatDate(activeRequest.contract_start) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Contract End">
            {{ formatDate(activeRequest.contract_end) }}
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
.leave-overview-page {
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
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  background: linear-gradient(
    180deg,
    var(--color-card) 0%,
    color-mix(in srgb, var(--hover-bg) 28%, var(--color-card) 72%) 100%
  );
}

.summary-card__label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted-color);
}

.summary-card__value {
  margin: 8px 0 0;
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--text-color);
}

.leave-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  box-shadow: 0 14px 36px var(--card-shadow);
}

.leave-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.leave-card__title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--text-color);
}

.leave-card__subtitle {
  margin: 4px 0 0;
  color: var(--muted-color);
  font-size: 13px;
}

.leave-card__count {
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

.filter-badge {
  margin-left: 6px;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 11px;
  line-height: 18px;
  background: color-mix(
    in srgb,
    var(--color-primary) 20%,
    var(--color-card) 80%
  );
}

.table-shell {
  min-height: 220px;
}

.leave-table {
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

@media (max-width: 768px) {
  .leave-card__header,
  .detail-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination-row {
    justify-content: flex-start;
  }
}
</style>
