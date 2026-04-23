<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import {
  ElMessage,
  ElPagination,
  ElButton,
  ElDialog,
  ElInput,
  ElForm,
  ElFormItem,
  ElDatePicker,
} from "element-plus";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeAvatarCell from "~/components/table-edit/cells/EmployeeAvatarCell.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  LeaveRequestDTO,
  LeaveRequestListParams,
  LeaveApproveDTO,
  LeaveRejectDTO,
} from "~/api/hr_admin/leave/dto";
import type { ColumnConfig } from "~/components/types/tableEdit";

const hrms = hrmsAdminService();

const loading = ref(false);
const hasFetchedOnce = ref(false);
const requests = ref<LeaveRequestDTO[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const dateRange = ref<[string, string] | null>(null);

const fetchData = async () => {
  loading.value = true;
  try {
    const params: LeaveRequestListParams = {
      page: page.value,
      limit: pageSize.value,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1],
    };
    const res = await hrms.leaveRequest.getPendingRequests(params);
    requests.value = res.items;
    total.value = res.total;
    hasFetchedOnce.value = true;
  } catch (e: any) {
    ElMessage.error(e?.message || "Failed to fetch leave requests");
  } finally {
    loading.value = false;
  }
};

onMounted(fetchData);
watch([page, pageSize, dateRange], fetchData);

const columns = computed<ColumnConfig<LeaveRequestDTO>[]>(() => [
  {
    label: "Employee",
    field: "employee_id",
    minWidth: 180,
    useSlot: true,
    slotName: "employee",
  },
  { label: "Type", field: "leave_type", minWidth: 120 },
  { label: "From", field: "start_date", minWidth: 120 },
  { label: "To", field: "end_date", minWidth: 120 },
  { label: "Reason", field: "reason", minWidth: 180 },
  { label: "Status", field: "status", minWidth: 120 },
  {
    label: "Actions",
    field: "actions" as any,
    minWidth: 180,
    useSlot: true,
    slotName: "actions",
    align: "center",
  },
]);

// Approve/Reject Dialog State
const dialogVisible = ref(false);
const dialogType = ref<"approve" | "reject">("approve");
const currentRequest = ref<LeaveRequestDTO | null>(null);
const approveForm = ref<{ comment: string }>({ comment: "" });
const rejectForm = ref<{ comment: string }>({ comment: "" });
const dialogLoading = ref(false);

function openApprove(row: LeaveRequestDTO) {
  dialogType.value = "approve";
  currentRequest.value = row;
  approveForm.value = { comment: "" };
  dialogVisible.value = true;
}
function openReject(row: LeaveRequestDTO) {
  dialogType.value = "reject";
  currentRequest.value = row;
  rejectForm.value = { comment: "" };
  dialogVisible.value = true;
}
async function handleApprove() {
  if (!currentRequest.value) return;
  dialogLoading.value = true;
  try {
    const payload: LeaveApproveDTO = { comment: approveForm.value.comment };
    await hrms.leaveRequest.approveRequest(currentRequest.value.id, payload);
    ElMessage.success("Leave approved");
    dialogVisible.value = false;
    fetchData();
  } catch (e: any) {
    ElMessage.error(e?.message || "Failed to approve");
  } finally {
    dialogLoading.value = false;
  }
}
async function handleReject() {
  if (!currentRequest.value) return;
  dialogLoading.value = true;
  try {
    const payload: LeaveRejectDTO = { comment: rejectForm.value.comment };
    await hrms.leaveRequest.rejectRequest(currentRequest.value.id, payload);
    ElMessage.success("Leave rejected");
    dialogVisible.value = false;
    fetchData();
  } catch (e: any) {
    ElMessage.error(e?.message || "Failed to reject");
  } finally {
    dialogLoading.value = false;
  }
}
</script>

<template>
  <TableCard
    title="Pending Leave Reviews"
    description="Review and take action on pending leave requests."
  >
    <template #header-right>
      <ElDatePicker
        v-model="dateRange"
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
      :data="requests"
      :columns="columns"
      :loading="loading"
      :hasFetchedOnce="hasFetchedOnce"
      :smartProps="{ border: true, stripe: true }"
    >
      <template #employee="{ row }">
        <EmployeeAvatarCell :row="row" />
        <span style="margin-left: 8px">{{
          row.full_name || row.employee_id
        }}</span>
      </template>
      <template #actions="{ row }">
        <ElButton size="small" type="success" @click="openApprove(row)"
          >Approve</ElButton
        >
        <ElButton
          size="small"
          type="danger"
          @click="openReject(row)"
          style="margin-left: 8px"
          >Reject</ElButton
        >
      </template>
    </SmartTable>
    <div style="margin-top: 16px; text-align: right">
      <ElPagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="prev, pager, next, sizes"
        background
        small
      />
    </div>
  </TableCard>

  <ElDialog
    v-model="dialogVisible"
    :title="dialogType === 'approve' ? 'Approve Leave' : 'Reject Leave'"
    width="400px"
    :close-on-click-modal="false"
  >
    <ElForm
      v-if="dialogType === 'approve'"
      :model="approveForm"
      label-width="120px"
    >
      <ElFormItem label="Comment">
        <ElInput
          v-model="approveForm.comment"
          :type="'text'"
          type="textarea"
          rows="2"
        />
      </ElFormItem>
    </ElForm>
    <ElForm v-else :model="rejectForm" label-width="120px">
      <ElFormItem label="Comment">
        <ElInput
          v-model="rejectForm.comment"
          :type="'text'"
          type="textarea"
          rows="2"
        />
      </ElFormItem>
    </ElForm>
    <template #footer>
      <ElButton @click="dialogVisible = false">Cancel</ElButton>
      <ElButton
        v-if="dialogType === 'approve'"
        type="success"
        :loading="dialogLoading"
        @click="handleApprove"
        >Approve</ElButton
      >
      <ElButton
        v-else
        type="danger"
        :loading="dialogLoading"
        @click="handleReject"
        >Reject</ElButton
      >
    </template>
  </ElDialog>
</template>
