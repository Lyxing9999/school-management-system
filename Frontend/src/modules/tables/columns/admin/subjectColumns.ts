import { ElInput } from "element-plus";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AdminSubjectDataDTO } from "~/api/admin/subject/subject.dto";

export const subjectColumns: ColumnConfig<AdminSubjectDataDTO>[] = [
  {
    field: "name",
    label: "Name",
    minWidth: "160px",
    sortable: true,
    controls: false,
    autoSave: true,
    revertSlots: true,
    component: ElInput,
    componentProps: {
      placeholder: "Enter subject name",
      class: "w-full",
    },
  },
  {
    field: "code",
    label: "Code",
    minWidth: "120px",
    sortable: true,
    controls: false,
    autoSave: true,
    revertSlots: true,
    component: ElInput,
    componentProps: {
      placeholder: "E.g. MATH",
      class: "w-full",
    },
  },
  {
    field: "description",
    label: "Description",
    minWidth: "240px",
    controls: true,
    autoSave: true,
    revertSlots: true,
    component: ElInput,
    componentProps: {
      type: "textarea",
      autosize: { minRows: 1, maxRows: 3 },
      placeholder: "Add description…",
      maxlength: 200,
      showWordLimit: true,
      resize: "none",
      class: "w-full",
    },
  },
  {
    field: "allowed_grade_levels",
    label: "Allowed Grades",
    minWidth: "200px",
    useSlot: true,
    slotName: "allowedGrades",
  },
  {
    field: "is_active",
    label: "Status",
    width: "120px",
    align: "center",
    useSlot: true,
    slotName: "status",
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
