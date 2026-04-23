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
  LeaveRequestDTO,
  LeaveRequestListParams,
  LeaveRequestStatus,
  LeaveSummaryDTO,
} from "~/api/hr_admin/leave/dto";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const leaveService = hrmsAdminService().leaveRequest;
const router = useRouter();

const loadingList = ref(false);
const loadingSummary = ref(false);
const rows = ref<LeaveRequestDTO[]>([]);
const summary = ref<LeaveSummaryDTO | null>(null);

const detailDialogVisible = ref(false);
const activeRow = ref<LeaveRequestDTO | null>(null);

const pagination = reactive({
  page: 1,
  limit: 10,
  total: 0,
});

const filters = reactive<{
  status: LeaveRequestStatus | "";
  start_date: string;
  end_date: string;
}>({
  status: "",
  start_date: "",
  end_date: "",
});

const loading = computed(() => loadingList.value || loadingSummary.value);

const hasFilters = computed(() =>
  Boolean(filters.status || filters.start_date || filters.end_date),
);

const statCards = computed(() => [
  {
    label: "Total Requests",
    value: summary.value?.total_requests ?? 0,
    hint: "All leave requests in your account",
  },
  {
    label: "Pending",
    value: summary.value?.pending ?? 0,
    hint: "Requests waiting for review",
  },
  {
    label: "Approved",
    value: summary.value?.approved ?? 0,
    hint: "Approved leave requests",
  },
  {
    label: "Approved Days",
    value: Number(summary.value?.total_approved_days ?? 0).toFixed(1),
    hint: "Total approved leave duration",
  },
]);

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
    status: filters.status || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
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

function leaveTypeLabel(value?: string | null): string {
  if (!value) return "-";

  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

async function fetchSummary() {
  loadingSummary.value = true;
  try {
    summary.value = await leaveService.getMySummary();
  } catch {
    ElMessage.error("Failed to load leave summary");
  } finally {
    loadingSummary.value = false;
  }
}

async function fetchHistory(page = pagination.page, limit = pagination.limit) {
  loadingList.value = true;

  try {
    const response = await leaveService.getMyRequests(buildParams(page, limit));

    rows.value = response.items ?? [];
    pagination.total = response.total ?? rows.value.length;
    pagination.page = response.page ?? page;
    pagination.limit = response.page_size ?? limit;
  } catch {
    ElMessage.error("Failed to load leave history");
  } finally {
    loadingList.value = false;
  }
}

async function loadPage() {
  await Promise.all([
    fetchSummary(),
    fetchHistory(pagination.page, pagination.limit),
  ]);
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

function openDetail(row: LeaveRequestDTO) {
  activeRow.value = row;
  detailDialogVisible.value = true;
}

function closeDetail() {
  detailDialogVisible.value = false;
  activeRow.value = null;
}

function refreshPage() {
  void loadPage();
}

onMounted(() => {
  void loadPage();
});
</script>

<template>
  <div class="employee-leave-history-page">
    <OverviewHeader
      title="Leave History"
      description="My leave history with summary and filters"
      :backPath="ROUTES.EMPLOYEE.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="refreshPage">
          Refresh
        </BaseButton>

        <BaseButton
          plain
          :disabled="loading"
          @click="router.push(ROUTES.EMPLOYEE.LEAVE_REQUEST)"
        >
          Request Leave
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
        <el-card class="summary-card" shadow="never" v-loading="loadingSummary">
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
              Filter by status and period, then browse your leave records.
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
        <BaseButton type="primary" :loading="loadingList" @click="applyFilters">
          Apply Filters
        </BaseButton>
        <BaseButton
          plain
          :disabled="loadingList || !hasFilters"
          @click="resetFilters"
        >
          Reset
        </BaseButton>
      </div>

      <div class="table-shell" v-loading="loadingList">
        <ElEmpty
          v-if="!loadingList && rows.length === 0"
          description="No leave requests found"
        />

        <ElTable v-else :data="rows" stripe class="history-table">
          <ElTableColumn label="Leave Type" min-width="150">
            <template #default="{ row }">
              {{ leaveTypeLabel(row.leave_type) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Start Date" min-width="130">
            <template #default="{ row }">
              {{ formatDate(row.start_date) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="End Date" min-width="130">
            <template #default="{ row }">
              {{ formatDate(row.end_date) }}
            </template>
          </ElTableColumn>

          <ElTableColumn label="Days" width="90" align="right">
            <template #default="{ row }">
              {{ Number(row.total_days || 0).toFixed(1) }}
            </template>
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
      title="Leave Request Detail"
      width="760px"
      @close="closeDetail"
    >
      <template v-if="activeRow">
        <ElDescriptions :column="2" border>
          <ElDescriptionsItem label="Request ID">
            {{ activeRow.id }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Leave Type">
            {{ leaveTypeLabel(activeRow.leave_type) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Start Date">
            {{ formatDate(activeRow.start_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="End Date">
            {{ formatDate(activeRow.end_date) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Total Days">
            {{ Number(activeRow.total_days || 0).toFixed(1) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Paid Leave">
            {{ activeRow.is_paid ? "Yes" : "No" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Status">
            {{ String(activeRow.status || "-").toUpperCase() }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Manager User ID">
            {{ activeRow.manager_user_id || "-" }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Contract Start">
            {{ formatDate(activeRow.contract_start) }}
          </ElDescriptionsItem>
          <ElDescriptionsItem label="Contract End">
            {{ formatDate(activeRow.contract_end) }}
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
.employee-leave-history-page {
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
  margin: 8px 0 4px;
  font-size: 28px;
  line-height: 1;
  font-weight: 800;
  color: var(--color-dark);
}

.summary-card__hint {
  margin: 0;
  font-size: 12px;
  color: var(--muted-color);
}

.history-card {
  border-radius: 18px;
  border: 1px solid
    color-mix(in srgb, var(--color-primary-light-8) 82%, var(--color-card) 18%);
  box-shadow: 0 14px 36px var(--card-shadow);
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
  color: var(--muted-color);
  font-size: 13px;
}

.history-card__count {
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
