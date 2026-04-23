<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import {
  ElPagination,
  ElSelect,
  ElOption,
  ElDatePicker,
  ElTabs,
  ElTabPane,
} from "element-plus";
import TableCard from "~/components/cards/TableCard.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import EmployeeAvatarCell from "~/components/table-edit/cells/EmployeeAvatarCell.vue";
import InlineStatusCell from "~/components/table-edit/cells/InlineStatusCell.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  AttendanceDTO,
  AttendanceTeamListParams,
  WrongLocationReportParams,
} from "~/api/hr_admin/attendance/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

const hrms = hrmsAdminService();

// Team Attendance State
const loadingTeam = ref(false);
const hasFetchedTeam = ref(false);
const teamAttendances = ref<AttendanceDTO[]>([]);
const teamTotal = ref(0);
const teamPage = ref(1);
const teamPageSize = ref(10);
const teamStatus = ref<string | undefined>(undefined);
const teamDateRange = ref<[string, string] | null>(null);

// Wrong Location State
const loadingWrong = ref(false);
const hasFetchedWrong = ref(false);
const wrongLocationReports = ref<AttendanceDTO[]>([]);
const wrongTotal = ref(0);
const wrongPage = ref(1);
const wrongPageSize = ref(10);
const wrongStatus = ref<string | undefined>(undefined);
const wrongReviewStatus = ref<string | undefined>(undefined);
const wrongDateRange = ref<[string, string] | null>(null);

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
const reviewStatusOptions = [
  { label: "All", value: "" },
  { label: "Pending", value: "pending" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
];

const fetchTeam = async () => {
  loadingTeam.value = true;
  try {
    const params: AttendanceTeamListParams = {
      page: teamPage.value,
      limit: teamPageSize.value,
      status: teamStatus.value || undefined,
      start_date: teamDateRange.value?.[0],
      end_date: teamDateRange.value?.[1],
    };
    const res = await hrms.attendance.getTeamAttendances(params);
    teamAttendances.value = res.items;
    teamTotal.value = res.pagination.total;
    hasFetchedTeam.value = true;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loadingTeam.value = false;
  }
};

const fetchWrong = async () => {
  loadingWrong.value = true;
  try {
    const params: WrongLocationReportParams = {
      page: wrongPage.value,
      limit: wrongPageSize.value,
      status: wrongStatus.value || undefined,
      review_status: wrongReviewStatus.value || undefined,
      start_date: wrongDateRange.value?.[0],
      end_date: wrongDateRange.value?.[1],
    };
    const res = await hrms.attendance.getWrongLocationReports(params);
    wrongLocationReports.value = res.items;
    wrongTotal.value = res.pagination.total;
    hasFetchedWrong.value = true;
  } catch {
    // API notifications are handled by service layer
  } finally {
    loadingWrong.value = false;
  }
};

onMounted(() => {
  fetchTeam();
  fetchWrong();
});

watch([teamPage, teamPageSize, teamStatus, teamDateRange], fetchTeam);
watch(
  [wrongPage, wrongPageSize, wrongStatus, wrongReviewStatus, wrongDateRange],
  fetchWrong,
);

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

const wrongColumns = computed(() => [
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
    label: "Wrong Location Reason",
    field: "wrong_location_reason",
    minWidth: 180,
  },
  {
    label: "Review Status",
    field: "location_review_status",
    minWidth: 140,
  },
  {
    label: "Admin Comment",
    field: "admin_comment",
    minWidth: 160,
  },
]);
</script>

<template>
  <ElTabs type="border-card">
    <ElTabPane label="Team Attendance">
      <TableCard
        title="Team Attendance"
        description="View and filter your team's attendance records."
      >
        <template #header-right>
          <ElSelect
            v-model="teamStatus"
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
            v-model="teamDateRange"
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
          :data="teamAttendances"
          :columns="columns"
          :loading="loadingTeam"
          :hasFetchedOnce="hasFetchedTeam"
          :smartProps="{ border: true, stripe: true }"
        >
          <template #employee="{ row }">
            <EmployeeAvatarCell :row="row" />
            <span style="margin-left: 8px">{{
              displayRelation(row.employee_name || row.full_name, row.employee_id)
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
            v-model:current-page="teamPage"
            v-model:page-size="teamPageSize"
            :total="teamTotal"
            :page-sizes="[10, 20, 50]"
            layout="prev, pager, next, sizes"
            background
            small
          />
        </div>
      </TableCard>
    </ElTabPane>
    <ElTabPane label="Wrong Location Reports">
      <TableCard
        title="Wrong Location Reports"
        description="Attendance records flagged for wrong location."
      >
        <template #header-right>
          <ElSelect
            v-model="wrongStatus"
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
          <ElSelect
            v-model="wrongReviewStatus"
            placeholder="Review Status"
            style="width: 140px; margin-right: 8px"
          >
            <ElOption
              v-for="opt in reviewStatusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </ElSelect>
          <ElDatePicker
            v-model="wrongDateRange"
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
          :data="wrongLocationReports"
          :columns="wrongColumns"
          :loading="loadingWrong"
          :hasFetchedOnce="hasFetchedWrong"
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
            v-model:current-page="wrongPage"
            v-model:page-size="wrongPageSize"
            :total="wrongTotal"
            :page-sizes="[10, 20, 50]"
            layout="prev, pager, next, sizes"
            background
            small
          />
        </div>
      </TableCard>
    </ElTabPane>
  </ElTabs>
</template>
