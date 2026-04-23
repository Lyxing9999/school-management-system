<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import { ElPagination, ElDatePicker } from "element-plus";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeAvatarCell from "~/components/table-edit/cells/EmployeeAvatarCell.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  LeaveRequestDTO,
  LeaveRequestListParams,
} from "~/api/hr_admin/leave/dto";
import type { ColumnConfig } from "~/components/types/tableEdit";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

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
    const res = await hrms.leaveRequest.getRequests(params);
    requests.value = res.items;
    total.value = res.total;
    hasFetchedOnce.value = true;
  } catch {
    // API notifications are handled by service layer
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
]);
</script>

<template>
  <TableCard
    title="Leave Request History"
    description="View all leave requests submitted by your team."
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
