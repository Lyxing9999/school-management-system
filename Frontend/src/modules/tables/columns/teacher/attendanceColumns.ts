import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AttendanceEnriched } from "~/api/teacher/attendance/dto";
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
    render: (row: AttendanceEnriched) => formatDate(row.record_date as any),
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
    label: "Actions",
    slotName: "operation",
    operation: true,
    fixed: "right",
    width: "220",
    align: "center",
  },
];
