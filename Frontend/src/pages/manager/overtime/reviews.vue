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
} from "element-plus";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeAvatarCell from "~/components/table-edit/cells/EmployeeAvatarCell.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  OvertimeRequestDTO,
  OvertimeRequestListParams,
  OvertimeApproveDTO,
  OvertimeRejectDTO,
} from "~/api/hr_admin/overtime/dto";
import type { ColumnConfig } from "~/components/types/tableEdit";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

const hrms = hrmsAdminService();

const loading = ref(false);
const hasFetchedOnce = ref(false);
const requests = ref<OvertimeRequestDTO[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const dateRange = ref<[string, string] | null>(null);

const fetchData = async () => {
  loading.value = true;
  try {
    const params: OvertimeRequestListParams = {
      page: page.value,
      limit: pageSize.value,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1],
    };
    const res = await hrms.overtimeRequest.getPendingRequests(params);
    requests.value = res.items;
    total.value = res.total;
    hasFetchedOnce.value = true;
  } catch (e: any) {
    ElMessage.error(e?.message || "Failed to fetch overtime requests");
  } finally {
    loading.value = false;
  }
};

onMounted(fetchData);
watch([page, pageSize, dateRange], fetchData);

const columns = computed<ColumnConfig<OvertimeRequestDTO>[]>(() => [
  {
    label: "Employee",
    field: "employee_id",
    minWidth: 180,
    useSlot: true,
    slotName: "employee",
  },
  { label: "Date", field: "request_date", minWidth: 120 },
  { label: "Start Time", field: "start_time", minWidth: 100 },
  { label: "End Time", field: "end_time", minWidth: 100 },
  { label: "Reason", field: "reason", minWidth: 180 },
  { label: "Status", field: "status", minWidth: 120 },
  // Type assertion for actions column
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
const currentRequest = ref<OvertimeRequestDTO | null>(null);
const approveForm = ref<{ approved_hours: number; comment: string }>({
  approved_hours: 0,
  comment: "",
});
const rejectForm = ref<{ comment: string }>({ comment: "" });
const dialogLoading = ref(false);

function openApprove(row: OvertimeRequestDTO) {
  dialogType.value = "approve";
  currentRequest.value = row;
  approveForm.value = { approved_hours: row.approved_hours || 0, comment: "" };
  dialogVisible.value = true;
}
function openReject(row: OvertimeRequestDTO) {
  dialogType.value = "reject";
  currentRequest.value = row;
  rejectForm.value = { comment: "" };
  dialogVisible.value = true;
}
async function handleApprove() {
  if (!currentRequest.value) return;
  dialogLoading.value = true;
  try {
    const payload: OvertimeApproveDTO = {
      approved_hours: approveForm.value.approved_hours,
      comment: approveForm.value.comment,
    };
    await hrms.overtimeRequest.approveRequest(currentRequest.value.id, payload);
    ElMessage.success("Overtime approved");
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
    const payload: OvertimeRejectDTO = { comment: rejectForm.value.comment };
    await hrms.overtimeRequest.rejectRequest(currentRequest.value.id, payload);
    ElMessage.success("Overtime rejected");
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
    title="Pending Overtime Approvals"
    description="Review and take action on pending overtime requests."
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
          displayRelation(row.employee_name || row.full_name, row.employee_id)
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
    :title="dialogType === 'approve' ? 'Approve Overtime' : 'Reject Overtime'"
    width="400px"
    :close-on-click-modal="false"
  >
    <ElForm
      v-if="dialogType === 'approve'"
      :model="approveForm"
      label-width="120px"
    >
      <ElFormItem label="Approved Hours">
        <ElInput
          v-model.number="approveForm.approved_hours"
          type="number"
          min="0"
        />
      </ElFormItem>
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
