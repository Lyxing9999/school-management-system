import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AttendanceEnriched } from "~/api/teacher/dto.ts";
import { ElTag } from "element-plus";
import { formatDate } from "~/utils/formatDate";
const getStatusTagType = (status: string) => {
  if (status === "present") return "success";
  if (status === "excused") return "warning";
  return "danger";
};

export const attendanceColumns: ColumnConfig<AttendanceEnriched>[] = [
  {
    key: "student",
    label: "Student",
    field: "student_name",
    render: (row: AttendanceEnriched) =>
      row.student_name || row.student_id || "Unknown",
  },
  {
    key: "record_date",
    label: "Date",
    field: "record_date",
    render: (row: AttendanceEnriched) =>
      formatDate(row.record_date, "YYYY-MM-DD"),
  },
  {
    key: "status",
    label: "Status",
    field: "status",
    render: (row: AttendanceEnriched) => ({
      component: ElTag,
      componentProps: {
        type: getStatusTagType(row.status),
        size: "small",
        effect: "plain",
      },
      value: row.status,
    }),
  },
  {
    key: "created_at",
    label: "Created",
    field: "created_at",
    render: (row: AttendanceEnriched) => ({
      component: "span",
      componentProps: {
        style: "font-size: 12px; color: var(--muted-color);",
      },
      value: formatDate(row.created_at),
    }),
  },
  {
    key: "updated_at",
    label: "Updated",
    field: "updated_at",
    render: (row: AttendanceEnriched) => ({
      component: "span",
      componentProps: {
        style: "font-size: 12px; color: var(--muted-color);",
      },
      value: formatDate(row.updated_at),
    }),
  },
  {
    field: "id",
    operation: true,
    label: "Operation",
    inlineEditActive: false,
    align: "center",
    minWidth: "200px",
    smartProps: {},
  },
];
