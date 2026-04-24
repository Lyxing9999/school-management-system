// frontend/src/modules/tables/columns/hr_admin/overtimeColumns.ts
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { OvertimeRequestDTO } from "~/api/hr_admin/overtime/dto";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";

dayjs.extend(duration);

export const overtimeColumns: ColumnConfig<OvertimeRequestDTO>[] = [
  {
    field: "employee_id",
    label: "Employee",
    width: "150px",
    visible: true,
    sortable: false,
    render: (row: OvertimeRequestDTO) =>
      displayRelation(row.employee_name, row.employee_id),
  },
  {
    field: "request_date",
    label: "Date",
    width: "130px",
    visible: true,
    sortable: true,
    render: (row: OvertimeRequestDTO) => {
      return dayjs(row.request_date).format("MMM DD, YYYY");
    },
  },
  {
    field: "start_time",
    label: "Start Time",
    width: "120px",
    visible: true,
    sortable: false,
    render: (row: OvertimeRequestDTO) => {
      return dayjs(row.start_time).format("HH:mm");
    },
  },
  {
    field: "end_time",
    label: "End Time",
    width: "120px",
    visible: true,
    sortable: false,
    render: (row: OvertimeRequestDTO) => {
      return dayjs(row.end_time).format("HH:mm");
    },
  },
  {
    field: "approved_hours",
    label: "Hours",
    width: "80px",
    visible: true,
    sortable: false,
    render: (row: OvertimeRequestDTO) => {
      const start = dayjs(row.start_time);
      const end = dayjs(row.end_time);
      const fallback =
        start.isValid() && end.isValid()
          ? Number((end.diff(start, "minute") / 60).toFixed(1))
          : 0;
      const hours = row.approved_hours > 0 ? row.approved_hours : fallback;
      return `${Number(hours).toFixed(1)}h`;
    },
  },
  {
    field: "reason",
    label: "Reason",
    minWidth: "200px",
    visible: true,
    sortable: false,
  },
  {
    field: "status",
    label: "Status",
    width: "120px",
    visible: true,
    sortable: true,
    slotName: "status",
  },
  {
    field: "manager_comment",
    label: "Manager Comment",
    minWidth: "180px",
    visible: false,
    sortable: false,
  },
  {
    field: "submitted_at",
    label: "Submitted",
    width: "160px",
    visible: true,
    sortable: true,
    render: (row: OvertimeRequestDTO) => {
      return dayjs(row.submitted_at).format("MMM DD, HH:mm");
    },
  },
  {
    field: "id",
    operation: true,
    label: "Actions",
    width: "250px",
    fixed: "right",
    visible: true,
    slotName: "operation",
  },
];
