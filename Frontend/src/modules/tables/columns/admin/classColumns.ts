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
    field: "teacher_name",
    align: "left",
    minWidth: "160px",
    render: (row: AdminClassDataDTO) =>
      h("span", row.teacher_name || "No teacher"),
  },
  {
    label: "Enrolled",
    field: "enrolled_count",
    align: "center",
    width: "110px",
    render: (row: AdminClassDataDTO) =>
      h("span", row.enrolled_count?.toString() || "0"),
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
    field: "id",
    operation: true,
    label: "Operation",
    inlineEditActive: false,
    // fixed: "right", // keep on desktop if you want; see note below
    align: "center",
    minWidth: "200px",
  },
];
