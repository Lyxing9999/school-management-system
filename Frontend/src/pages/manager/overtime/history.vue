<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import {
  ElMessage,
  ElPagination,
  ElDatePicker,
  ElSelect,
  ElOption,
} from "element-plus";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeAvatarCell from "~/components/table-edit/cells/EmployeeAvatarCell.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  OvertimeRequestDTO,
  OvertimeRequestListParams,
} from "~/api/hr_admin/overtime/dto";
import type { ColumnConfig } from "~/components/types/tableEdit";

const hrms = hrmsAdminService();

const loading = ref(false);
const hasFetchedOnce = ref(false);
const requests = ref<OvertimeRequestDTO[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const dateRange = ref<[string, string] | null>(null);
const status = ref<string>("");

const statusOptions = [
  { label: "All", value: "" },
  { label: "Pending", value: "pending" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
  { label: "Cancelled", value: "cancelled" },
];

const fetchData = async () => {
  loading.value = true;
  try {
    const params: OvertimeRequestListParams = {
      page: page.value,
      limit: pageSize.value,
      status: status.value || undefined,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1],
    };
    const res = await hrms.overtimeRequest.getRequests(params);
    requests.value = res.items;
    total.value = res.total;
    hasFetchedOnce.value = true;
  } catch (e: any) {
    ElMessage.error(e?.message || "Failed to fetch overtime history");
  } finally {
    loading.value = false;
  }
};

onMounted(fetchData);
watch([page, pageSize, status, dateRange], fetchData);

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
  { label: "Approved Hours", field: "approved_hours", minWidth: 120 },
  { label: "Manager Comment", field: "manager_comment", minWidth: 160 },
]);
</script>

<template>
  <TableCard
    title="Overtime History"
    description="View all overtime requests for your team."
  >
    <template #header-right>
      <ElSelect
        v-model="status"
        placeholder="Status"
        style="width: 140px; margin-right: 8px"
      >
        <ElOption
          v-for="opt in statusOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </ElSelect>
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
</template>
