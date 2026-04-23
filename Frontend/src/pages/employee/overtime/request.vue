<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  ElButton,
  ElCard,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElDatePicker,
  ElTimePicker,
  ElTable,
  ElTableColumn,
  ElTag,
  ElPagination,
  ElLoading,
  ElEmpty,
} from "element-plus";
import type { FormInstance } from "element-plus";
import { Plus, Delete, Clock } from "@element-plus/icons-vue";
import { useOvertimeStore } from "~/stores/overtimeStore";
import type { OvertimeRequestCreateDTO } from "~/api/hr_admin/overtime/dto";

definePageMeta({ layout: "default" });

const overtimeStore = useOvertimeStore();
const router = useRouter();

// Dialog states
const createDialogVisible = ref(false);
const detailDialogVisible = ref(false);
const cancelReasonDialogVisible = ref(false);

// Forms
const createFormRef = ref<FormInstance>();
const createForm = ref<OvertimeRequestCreateDTO>({
  request_date: "",
  start_time: "",
  end_time: "",
  reason: "",
});

const cancelForm = ref({
  reason: "",
});

const cancelingRequestId = ref<string | null>(null);

// Computed properties
const mySummary = computed(() => overtimeStore.mySummary);
const myRequests = computed(() => overtimeStore.myRequests);
const requestDetail = computed(() => overtimeStore.requestDetail);
const isLoadingMyRequests = computed(() =>
  overtimeStore.isLoading("getMyRequests"),
);
const isLoadingCreateRequest = computed(() =>
  overtimeStore.isLoading("createRequest"),
);
const isLoadingDetail = computed(() => overtimeStore.isLoading("getRequest"));
const isLoadingCancel = computed(() =>
  overtimeStore.isLoading("cancelRequest"),
);

const paginationProps = computed(() => ({
  currentPage: overtimeStore.pagination.page,
  pageSize: overtimeStore.pagination.limit,
  total: overtimeStore.pagination.total,
}));

// Methods
function openCreateDialog() {
  createForm.value = {
    request_date: "",
    start_time: "",
    end_time: "",
    reason: "",
  };
  createDialogVisible.value = true;
}

function closeCreateDialog() {
  createDialogVisible.value = false;
  createForm.value = {
    request_date: "",
    start_time: "",
    end_time: "",
    reason: "",
  };
  createFormRef.value?.clearValidate();
}

async function submitCreateRequest() {
  if (!createFormRef.value) return;

  try {
    await createFormRef.value.validate();
    await overtimeStore.createRequest(createForm.value);
    ElMessage.success("Overtime request created successfully");
    closeCreateDialog();
    await overtimeStore.fetchMyList();
  } catch (error: any) {
    if (error?.message && !error.response) {
      ElMessage.error(overtimeStore.getError("createRequest") || error.message);
    }
  }
}

async function viewDetail(id: string) {
  try {
    await overtimeStore.fetchOne(id);
    detailDialogVisible.value = true;
  } catch (error) {
    ElMessage.error("Failed to load request detail");
  }
}

function closeDetailDialog() {
  detailDialogVisible.value = false;
  overtimeStore.clearDetail();
}

function openCancelDialog(id: string) {
  cancelingRequestId.value = id;
  cancelForm.value = { reason: "" };
  cancelReasonDialogVisible.value = true;
}

function closeCancelDialog() {
  cancelReasonDialogVisible.value = false;
  cancelingRequestId.value = null;
  cancelForm.value = { reason: "" };
}

async function submitCancel() {
  if (!cancelingRequestId.value) return;

  try {
    await ElMessageBox.confirm(
      "Are you sure you want to cancel this overtime request?",
      "Confirm Cancel",
      {
        confirmButtonText: "Yes, Cancel Request",
        cancelButtonText: "No",
        type: "warning",
      },
    );

    await overtimeStore.cancelRequest(cancelingRequestId.value, {
      reason: cancelForm.value.reason || undefined,
    });
    ElMessage.success("Overtime request cancelled successfully");
    closeCancelDialog();
    await overtimeStore.fetchMyList();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(
        overtimeStore.getError("cancelRequest") || "Failed to cancel request",
      );
    }
  }
}

function formatTime(time: string) {
  if (!time) return "—";
  return time;
}

function formatDate(date: string) {
  if (!date) return "—";
  return new Date(date).toLocaleDateString();
}

function statusTagType(
  status: string,
): "success" | "info" | "warning" | "danger" {
  switch (status?.toLowerCase()) {
    case "approved":
      return "success";
    case "rejected":
      return "danger";
    case "cancelled":
      return "info";
    case "pending":
      return "warning";
    default:
      return "info";
  }
}

// Page initialization
onMounted(async () => {
  try {
    await Promise.all([
      overtimeStore.fetchMyList(),
      overtimeStore.fetchMySummary(),
    ]);
  } catch (error) {
    ElMessage.error("Failed to load overtime information");
  }
});

const handlePageChange = async (page: number) => {
  await overtimeStore.fetchMyList(page);
};
</script>

<template>
  <div class="employee-overtime-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>My Overtime Requests</h1>
        <p class="subtitle">Track and manage your overtime requests</p>
      </div>
      <ElButton type="primary" :icon="Plus" @click="openCreateDialog">
        Request Overtime
      </ElButton>
    </div>

    <!-- Summary Cards -->
    <div class="summary-grid" v-if="mySummary">
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Total Requests</div>
        </template>
        <div class="card-value">{{ mySummary.total_requests }}</div>
      </ElCard>
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Pending</div>
        </template>
        <div class="card-value pending">{{ mySummary.pending_count }}</div>
      </ElCard>
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Approved</div>
        </template>
        <div class="card-value approved">{{ mySummary.approved_count }}</div>
      </ElCard>
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Approved Hours</div>
        </template>
        <div class="card-value">{{ mySummary.approved_hours }}</div>
      </ElCard>
      <ElCard class="summary-card">
        <template #header>
          <div class="card-header">Approved Payment</div>
        </template>
        <div class="card-value">₱{{ mySummary.approved_payment }}</div>
      </ElCard>
    </div>

    <!-- Requests Table -->
    <ElCard class="requests-card">
      <template #header>
        <div class="card-title">My Requests</div>
      </template>

      <div v-if="isLoadingMyRequests" class="loading">
        <ElLoading fullscreen lock />
      </div>

      <ElEmpty v-else-if="!myRequests || myRequests.length === 0" />

      <ElTable v-else :data="myRequests" stripe>
        <ElTableColumn prop="request_date" label="Date" width="120">
          <template #default="{ row }">
            {{ formatDate(row.request_date) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="start_time" label="Start Time" width="120">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="end_time" label="End Time" width="120">
          <template #default="{ row }">
            {{ formatTime(row.end_time) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="reason" label="Reason" min-width="200" />
        <ElTableColumn prop="status" label="Status" width="100">
          <template #default="{ row }">
            <ElTag :type="statusTagType(row.status)">
              {{ row.status }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="approved_hours" label="Approved Hours" width="120">
          <template #default="{ row }">
            {{ row.approved_hours || "—" }}
          </template>
        </ElTableColumn>
        <ElTableColumn label="Actions" width="150" align="center">
          <template #default="{ row }">
            <ElButton
              link
              type="primary"
              size="small"
              @click="viewDetail(row.id)"
            >
              View
            </ElButton>
            <ElButton
              v-if="row.status === 'pending'"
              link
              type="danger"
              size="small"
              :icon="Delete"
              @click="openCancelDialog(row.id)"
            >
              Cancel
            </ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <div v-if="myRequests && myRequests.length > 0" class="pagination">
        <ElPagination
          :current-page="paginationProps.currentPage"
          :page-size="paginationProps.pageSize"
          :total="paginationProps.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </ElCard>

    <!-- Create Request Dialog -->
    <ElDialog
      v-model="createDialogVisible"
      title="Request Overtime"
      width="600px"
      @close="closeCreateDialog"
    >
      <ElForm ref="createFormRef" :model="createForm" label-width="120px">
        <ElFormItem
          label="Request Date"
          prop="request_date"
          :rules="[{ required: true, message: 'Date is required' }]"
        >
          <ElDatePicker
            v-model="createForm.request_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="Select date"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem
          label="Start Time"
          prop="start_time"
          :rules="[{ required: true, message: 'Start time is required' }]"
        >
          <ElTimePicker
            v-model="createForm.start_time"
            value-format="HH:mm:ss"
            placeholder="Select start time"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem
          label="End Time"
          prop="end_time"
          :rules="[{ required: true, message: 'End time is required' }]"
        >
          <ElTimePicker
            v-model="createForm.end_time"
            value-format="HH:mm:ss"
            placeholder="Select end time"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem
          label="Reason"
          prop="reason"
          :rules="[{ required: true, message: 'Reason is required' }]"
        >
          <ElInput
            v-model="createForm.reason"
            type="textarea"
            placeholder="Explain why you need overtime"
            rows="4"
          />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="closeCreateDialog">Cancel</ElButton>
        <ElButton
          type="primary"
          :loading="isLoadingCreateRequest"
          @click="submitCreateRequest"
        >
          Submit Request
        </ElButton>
      </template>
    </ElDialog>

    <!-- Detail Dialog -->
    <ElDialog
      v-model="detailDialogVisible"
      title="Request Details"
      width="700px"
      @close="closeDetailDialog"
    >
      <div v-if="requestDetail" class="detail-content">
        <div class="detail-row">
          <span class="label">Date:</span>
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
          <span class="label">Status:</span>
          <ElTag :type="statusTagType(requestDetail.status)">
            {{ requestDetail.status }}
          </ElTag>
        </div>
        <div class="detail-row">
          <span class="label">Reason:</span>
          <span class="value">{{ requestDetail.reason }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Approved Hours:</span>
          <span class="value">{{ requestDetail.approved_hours || "—" }}</span>
        </div>
        <div class="detail-row">
          <span class="label">Manager Comment:</span>
          <span class="value">{{ requestDetail.manager_comment || "—" }}</span>
        </div>
      </div>
    </ElDialog>

    <!-- Cancel Reason Dialog -->
    <ElDialog
      v-model="cancelReasonDialogVisible"
      title="Cancel Request"
      width="500px"
      @close="closeCancelDialog"
    >
      <ElForm label-width="80px">
        <ElFormItem label="Reason">
          <ElInput
            v-model="cancelForm.reason"
            type="textarea"
            placeholder="Optional: Explain why you're cancelling"
            rows="3"
          />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="closeCancelDialog">Cancel</ElButton>
        <ElButton
          type="danger"
          :loading="isLoadingCancel"
          @click="submitCancel"
        >
          Confirm Cancel
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.employee-overtime-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.subtitle {
  margin: 4px 0 0 0;
  color: #606266;
  font-size: 14px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  background: white;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-top: 10px;
}

.card-value.pending {
  color: #e6a23c;
}

.card-value.approved {
  color: #67c23a;
}

.requests-card {
  margin-bottom: 20px;
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
  border-bottom: 1px solid #ebeef5;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #606266;
}

.value {
  color: #303133;
}
</style>
