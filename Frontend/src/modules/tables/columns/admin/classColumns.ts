import { h } from "vue";
import { ElTag } from "element-plus";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AdminClassDataDTO } from "~/api/admin/class/class.dto";

function normalizeStatus(status?: string | null) {
  return (status || "").trim().toLowerCase();
}

function getStatusTagType(status?: string | null) {
  const s = normalizeStatus(status);
  if (["active", "enabled", "open"].includes(s)) return "success";
  if (["inactive", "disabled", "closed"].includes(s)) return "info";
  if (["archived", "deleted"].includes(s)) return "warning";
  return "danger";
}

function formatStatus(status?: string | null) {
  const s = normalizeStatus(status);
  if (!s) return "Unknown";
  // Title Case: "active" -> "Active"
  return s.charAt(0).toUpperCase() + s.slice(1);
}

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
    label: "Status",
    field: "status",
    align: "center",
    width: "110px",
    render: (row) =>
      h(
        ElTag,
        {
          type: getStatusTagType(row.status),
          effect: "plain",
          size: "small",
        },
        () => formatStatus(row.status)
      ),
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
