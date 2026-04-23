<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import {
  ElMessage,
  ElPagination,
  ElSelect,
  ElOption,
  ElDatePicker,
} from "element-plus";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeAvatarCell from "~/components/table-edit/cells/EmployeeAvatarCell.vue";
import InlineStatusCell from "~/components/table-edit/cells/InlineStatusCell.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  AttendanceDTO,
  AttendanceTeamListParams,
} from "~/api/hr_admin/attendance/dto";

const hrms = hrmsAdminService();

const loading = ref(false);
const hasFetchedOnce = ref(false);
const attendances = ref<AttendanceDTO[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const status = ref<string | undefined>(undefined);
const dateRange = ref<[string, string] | null>(null);

const statusOptions = [
  { label: "All", value: "" },
  { label: "Checked In", value: "checked_in" },
  { label: "Checked Out", value: "checked_out" },
  { label: "Late", value: "late" },
  { label: "Early Leave", value: "early_leave" },
  { label: "Absent", value: "absent" },
  { label: "Wrong Location Pending", value: "wrong_location_pending" },
  { label: "Wrong Location Approved", value: "wrong_location_approved" },
  { label: "Wrong Location Rejected", value: "wrong_location_rejected" },
];

const fetchData = async () => {
  loading.value = true;
  try {
    const params: AttendanceTeamListParams = {
      page: page.value,
      limit: pageSize.value,
      status: status.value || undefined,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1],
    };
    const res = await hrms.attendance.getTeamAttendances(params);
    attendances.value = res.items;
    total.value = res.pagination.total;
    hasFetchedOnce.value = true;
  } catch (e: any) {
    ElMessage.error(e?.message || "Failed to fetch team attendance");
  } finally {
    loading.value = false;
  }
};

onMounted(fetchData);

watch([page, pageSize, status, dateRange], fetchData);

const columns = computed(() => [
  {
    label: "Employee",
    field: "employee_id",
    minWidth: 180,
    useSlot: true,
    slotName: "employee",
  },
  {
    label: "Date",
    field: "attendance_date",
    minWidth: 120,
  },
  {
    label: "Check In",
    field: "check_in_time",
    minWidth: 120,
  },
  {
    label: "Check Out",
    field: "check_out_time",
    minWidth: 120,
  },
  {
    label: "Status",
    field: "status",
    minWidth: 140,
    useSlot: true,
    slotName: "status",
  },
  {
    label: "Late (min)",
    field: "late_minutes",
    minWidth: 100,
  },
  {
    label: "Early Leave (min)",
    field: "early_leave_minutes",
    minWidth: 120,
  },
]);
</script>

<template>
  <TableCard
    title="Team Attendance"
    description="View and filter your team's attendance records."
  >
    <template #header-right>
      <ElSelect
        v-model="status"
        placeholder="Status"
        style="width: 160px; margin-right: 12px"
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
      :data="attendances"
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
      <template #status="{ row }">
        <InlineStatusCell
          :row-id="row.id"
          :value="row.status"
          :editing-row-id="null"
          :draft="row.status"
          :options="statusOptions.filter((o) => o.value)"
          :tag-type="
            (v) => {
              switch (v) {
                case 'checked_in':
                  return 'info';
                case 'checked_out':
                  return 'success';
                case 'late':
                  return 'warning';
                case 'early_leave':
                  return 'warning';
                case 'absent':
                  return 'danger';
                case 'wrong_location_pending':
                  return 'warning';
                case 'wrong_location_approved':
                  return 'success';
                case 'wrong_location_rejected':
                  return 'danger';
                default:
                  return '';
              }
            }
          "
          :format-label="
            (v) => statusOptions.find((o) => o.value === v)?.label || v
          "
          disabled
        />
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
