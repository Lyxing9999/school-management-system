import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AdminSubjectDataDTO } from "~/api/admin/subject/subject.dto";
// ------------------ Subject Table Columns ------------------

export const subjectColumns = computed<ColumnConfig<AdminSubjectDataDTO>[]>(
  () => [
    {
      field: "name",
      label: "Name",
      minWidth: 140,
    },
    {
      field: "code",
      label: "Code",
      minWidth: 120,
    },
    {
      field: "description",
      label: "Description",
      minWidth: 180,
      useSlots: true,
      slotName: "description",
    },
    {
      field: "allowed_grade_levels",
      label: "Allowed Grades",
      minWidth: 160,
      useSlots: true,
      slotName: "allowedGrades",
    },
    {
      field: "is_active",
      label: "Status",
      align: "center",
      operation: true, 
    },
  ]
);
