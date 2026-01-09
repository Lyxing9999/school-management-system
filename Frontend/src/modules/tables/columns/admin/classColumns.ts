import { h } from "vue";

import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AdminClassDataDTO } from "~/api/admin/class/class.dto";

export const classColumns: ColumnConfig<AdminClassDataDTO>[] = [
  {
    label: "Name",
    field: "name",
    align: "left",
    minWidth: "160px",
    render: (row) => h("span", row.name || "—"),
  },
  {
    label: "Teacher",
    field: "homeroom_teacher_name",
    align: "left",
    minWidth: "160px",
    render: (row) => h("span", row.homeroom_teacher_name || "No teacher"),
  },
  {
    field: "status",
    label: "Status",
    width: "130px",
    useSlot: true,
    slotName: "status",
  },
  {
    label: "Enrolled",
    field: "enrolled_count",
    align: "center",
    width: "110px",
    render: (row) => h("span", String(row.enrolled_count ?? 0)),
  },
  {
    label: "Subjects",
    field: "subject_ids",
    align: "center",
    width: "110px",
    render: (row) => h("span", String(row.subject_ids?.length ?? 0)),
  },
  {
    label: "Max Students",
    field: "max_students",
    align: "center",
    width: "130px",
    inlineEditActive: false,
    render: (row) => h("span", String(row.max_students ?? "—")),
  },
  {
    field: "id",
    label: "Operation",
    align: "center",
    width: "220px",
    operation: true,
    inlineEditActive: false,
    useSlot: true,
    slotName: "operation",
  },
];
