// frontend/src/modules/tables/columns/hr_admin/leaveColumns.ts
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { LeaveDTO } from "~/api/hr_admin/leave/dto";
import dayjs from "dayjs";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

export const leaveColumns: ColumnConfig<LeaveDTO>[] = [
  {
    prop: "id",
    label: "ID",
    width: 100,
    visible: false,
  },
  {
    prop: "employee_id",
    label: "Employee",
    width: 150,
    visible: true,
    sortable: false,
    formatter: (row: LeaveDTO) =>
      displayRelation(row.employee_name, row.employee_id),
  },
  {
    prop: "leave_type",
    label: "Type",
    width: 120,
    visible: true,
    sortable: true,
    formatter: (row: LeaveDTO) => {
      const typeMap: Record<string, string> = {
        annual: "Annual",
        sick: "Sick",
        unpaid: "Unpaid",
        other: "Other",
      };
      return typeMap[row.leave_type] || row.leave_type;
    },
  },
  {
    prop: "start_date",
    label: "Start Date",
    width: 130,
    visible: true,
    sortable: true,
    formatter: (row: LeaveDTO) => {
      return dayjs(row.start_date).format("MMM DD, YYYY");
    },
  },
  {
    prop: "end_date",
    label: "End Date",
    width: 130,
    visible: true,
    sortable: true,
    formatter: (row: LeaveDTO) => {
      return dayjs(row.end_date).format("MMM DD, YYYY");
    },
  },
  {
    prop: "total_days",
    label: "Days",
    width: 80,
    visible: true,
    sortable: false,
    formatter: (row: LeaveDTO) => {
      const start = dayjs(row.start_date);
      const end = dayjs(row.end_date);
      return end.diff(start, "day") + 1;
    },
  },
  {
    prop: "reason",
    label: "Reason",
    minWidth: 200,
    visible: true,
    sortable: false,
  },
  {
    prop: "status",
    label: "Status",
    width: 120,
    visible: true,
    sortable: true,
    slotName: "status",
  },
  {
    prop: "is_paid",
    label: "Paid",
    width: 80,
    visible: true,
    sortable: false,
    formatter: (row: LeaveDTO) => (row.is_paid ? "Yes" : "No"),
  },
  {
    prop: "manager_comment",
    label: "Manager Comment",
    minWidth: 180,
    visible: false,
    sortable: false,
  },
  {
    prop: "lifecycle.created_at",
    label: "Submitted",
    width: 150,
    visible: true,
    sortable: true,
    formatter: (row: LeaveDTO) => {
      return dayjs(row.lifecycle.created_at).format("MMM DD, YYYY HH:mm");
    },
  },
  {
    prop: "operation",
    label: "Actions",
    width: 150,
    fixed: "right",
    slotName: "operation",
  },
];
