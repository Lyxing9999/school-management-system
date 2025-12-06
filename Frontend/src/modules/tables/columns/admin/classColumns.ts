import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AdminClassDataDTO } from "~/api/admin/class/class.dto";
export const classColumns: ColumnConfig<AdminClassDataDTO>[] = [
  {
    label: "Name",
    field: "name",
    align: "left",
    minWidth: "160px",
  },
  {
    label: "Teacher",
    field: "teacher_id",
    align: "left",
    minWidth: "160px",
    render: (row: AdminClassDataDTO) =>
      h("span", row.teacher_name || "No teacher"),
  },
  {
    label: "Students",
    field: "student_ids",
    align: "center",
    width: "110px",
    render: (row: AdminClassDataDTO) =>
      h("span", (row.student_ids?.length ?? 0).toString()),
  },
  {
    label: "Subjects",
    field: "subject_ids",
    align: "center",
    width: "110px",
    render: (row: AdminClassDataDTO) =>
      h("span", (row.subject_ids?.length ?? 0).toString()),
  },
  {
    inlineEditActive: false,
    label: "Max Students",
    field: "max_students",
    align: "center",
    width: "130px",
  },
  {
    label: "Actions",
    slotName: "operation",
    operation: true,
    fixed: "right",
    width: "220px",
    align: "center",
  },
];
