<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  ElButton,
  ElCard,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElTable,
  ElTableColumn,
  ElTag,
  ElPagination,
  ElLoading,
  ElEmpty,
  ElDatePicker,
} from "element-plus";
import { useOvertimeStore } from "~/stores/overtimeStore";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

definePageMeta({ layout: "default" });

const overtimeStore = useOvertimeStore();

// Dialog states
const detailDialogVisible = ref(false);

// Filters
const dateRange = ref<[string, string] | null>(null);

// Computed properties
const payrollApprovedRequests = computed(() => overtimeStore.payrollApproved);
const payrollSummary = computed(() => overtimeStore.payrollSummary);
const requestDetail = computed(() => overtimeStore.requestDetail);
const isLoadingApproved = computed(() =>
  overtimeStore.isLoading("getPayrollApprovedRequests"),
);
const isSummaryLoading = computed(() =>
  overtimeStore.isLoading("getPayrollOvertimeSummary"),
);
const isLoadingDetail = computed(() => overtimeStore.isLoading("getRequest"));

const paginationProps = computed(() => ({
  currentPage: overtimeStore.pagination.page,
  pageSize: overtimeStore.pagination.limit,
  total: overtimeStore.pagination.total,
}));

// Methods
async function viewDetail(id: string) {
  try {
    await overtimeStore.fetchOne(id);
    detailDialogVisible.value = true;
  } catch {
    // API notifications are handled by service/store layer
  }
}

function closeDetailDialog() {
  detailDialogVisible.value = false;
  overtimeStore.clearDetail();
}

function formatTime(time: string) {
  if (!time) return "—";
  return time;
}

function formatDate(date: string) {
  if (!date) return "—";
  return new Date(date).toLocaleDateString();
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
  }).format(amount);
}

// Page initialization
onMounted(async () => {
  try {
    await Promise.all([
      overtimeStore.fetchPayrollApproved(),
      overtimeStore.fetchPayrollSummary(),
    ]);
  } catch {
    // API notifications are handled by service/store layer
  }
});

const handlePageChange = async (page: number) => {
  await overtimeStore.fetchPayrollApproved(page);
};

const handleDateRangeChange = async () => {
  if (dateRange.value && dateRange.value.length === 2) {
    overtimeStore.setFilters({
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
    });
    await Promise.all([
      overtimeStore.fetchPayrollApproved(),
      overtimeStore.fetchPayrollSummary(),
    ]);
  }
};
</script>

<template>
  <div class="payroll-overtime-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Payroll Overtime Summary</h1>
        <p class="subtitle">Approved overtime for payroll processing</p>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-grid" v-if="payrollSummary && !isSummaryLoading">
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Total Approved Requests</div>
        </template>
        <div class="card-value">
          {{ payrollSummary.total_approved_requests }}
        </div>
      </ElCard>
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Total Approved Hours</div>
        </template>
        <div class="card-value">{{ payrollSummary.total_approved_hours }}</div>
      </ElCard>
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Total Payment</div>
        </template>
        <div class="card-value currency">
          {{ formatCurrency(payrollSummary.total_approved_payment) }}
        </div>
      </ElCard>
    </div>

    <!-- Loading Summary -->
    <div v-if="isSummaryLoading" class="loading">
      <ElLoading fullscreen lock />
    </div>

    <!-- Approved Requests Table -->
    <ElCard class="requests-card">
      <template #header>
        <div class="card-header-row">
          <div class="card-title">Approved Overtime Requests</div>
          <ElDatePicker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start date"
            end-placeholder="End date"
            @change="handleDateRangeChange"
            style="width: 300px"
          />
        </div>
      </template>

      <div v-if="isLoadingApproved" class="loading">
        <ElLoading fullscreen lock />
      </div>

      <ElEmpty
        v-else-if="
          !payrollApprovedRequests || payrollApprovedRequests.length === 0
        "
      />

      <ElTable v-else :data="payrollApprovedRequests" stripe>
        <ElTableColumn label="Employee" width="180">
          <template #default="{ row }">
            {{ displayRelation(row.employee_name, row.employee_id) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="request_date" label="Date" width="120">
          <template #default="{ row }">
            {{ formatDate(row.request_date) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="start_time" label="Start" width="90">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="end_time" label="End" width="90">
          <template #default="{ row }">
            {{ formatTime(row.end_time) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="approved_hours" label="Approved Hours" width="120">
          <template #default="{ row }">
            {{ row.approved_hours || "—" }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="calculated_payment" label="Payment" width="140">
          <template #default="{ row }">
            {{ formatCurrency(row.calculated_payment) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="day_type" label="Day Type" width="120">
          <template #default="{ row }">
            <ElTag type="info">{{ row.day_type }}</ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn label="Actions" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <ElButton
              link
              type="primary"
              size="small"
              @click="viewDetail(row.id)"
            >
              View
            </ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <div
        v-if="payrollApprovedRequests && payrollApprovedRequests.length > 0"
        class="pagination"
      >
        <ElPagination
          :current-page="paginationProps.currentPage"
          :page-size="paginationProps.pageSize"
          :total="paginationProps.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </ElCard>

    <!-- Detail Dialog -->
    <ElDialog
      v-model="detailDialogVisible"
      title="Request Details"
      width="700px"
      @close="closeDetailDialog"
    >
      <div v-if="requestDetail" class="detail-content">
        <div class="detail-row">
          <span class="label">Employee:</span>
          <span class="value">{{
            displayRelation(requestDetail.employee_name, requestDetail.employee_id)
          }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Request Date:</span>
          <span class="value">{{
            formatDate(requestDetail.request_date)
          }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Time:</span>
          <span class="value">
            {{ formatTime(requestDetail.start_time) }} -
            {{ formatTime(requestDetail.end_time) }}
          </span>
        </div>
        <div class="detail-row">
          <span class="label">Day Type:</span>
          <span class="value">{{ requestDetail.day_type }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Basic Salary:</span>
          <span class="value">
            {{ formatCurrency(requestDetail.basic_salary) }}
          </span>
        </div>
        <div class="detail-row">
          <span class="label">Approved Hours:</span>
          <span class="value">{{ requestDetail.approved_hours || "—" }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Calculated Payment:</span>
          <span class="value">
            {{ formatCurrency(requestDetail.calculated_payment) }}
          </span>
        </div>
        <div class="detail-row">
          <span class="label">Status:</span>
          <ElTag type="success">{{ requestDetail.status }}</ElTag>
        </div>
        <div class="detail-row">
          <span class="label">Reason:</span>
          <span class="value">{{ requestDetail.reason }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Manager Comment:</span>
          <span class="value">{{ requestDetail.manager_comment || "—" }}</span>
        </div>
      </div>
    </ElDialog>
  </div>
</template>

<style scoped>
.payroll-overtime-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 4px 0 0 0;
  color: var(--muted-color);
  font-size: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  background: var(--color-card);
}

.card-header {
  font-weight: 600;
  color: var(--color-dark);
  font-size: 14px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--color-dark);
  margin-top: 10px;
}

.card-value.currency {
  color: var(--button-success-bg);
}

.requests-card {
  margin-bottom: 20px;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.pagination {
  margin-top: 16px;
  text-align: right;
}

.loading {
  position: relative;
  min-height: 200px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: var(--muted-color);
}

.value {
  color: var(--color-dark);
}
</style>
