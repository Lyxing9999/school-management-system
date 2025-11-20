import type { ColumnConfig } from "~/components/types/tableEdit";
import type { Field } from "~/components/types/form";
import { ElInput, ElDatePicker } from "element-plus";
import { h } from "vue";
import type {
  AdminCreateSubject,
  AdminUpdateSubject,
} from "~/api/admin/subject/dto";
import type { SubjectBaseDataDTO } from "~/api/types/subject.dto";
// ------------------ Subject Table Columns ------------------
export const subjectColumns: ColumnConfig<SubjectBaseDataDTO>[] = [
  {
    field: "name",
    label: "Subject Name",
    sortable: true,
    minWidth: "200px",
    inlineEditActive: true,
    autoSave: true,
    controls: false,

    rules: [
      { required: true, message: "Please input subject name", trigger: "blur" },
      { min: 2, message: "At least 2 characters", trigger: "blur" },
    ],
    component: ElInput,
    componentProps: { placeholder: "Enter subject name" },
  },
  {
    field: "teacher_id",
    label: "Teacher",
    sortable: true,
    minWidth: "120px",
    inlineEditActive: true,
    autoSave: true,
    rules: [{ required: true, message: "Teacher required", trigger: "blur" }],
    component: ElInput,
    componentProps: { placeholder: "Enter code" },
  },
  {
    field: "created_by",
    label: "Created By",
    inlineEditActive: true,
    controls: false,
    controlsSlot: false,
    minWidth: "140px", // flexible
    align: "center",
  },
  {
    field: "created_at",
    label: "Created At",
    inlineEditActive: true,
    minWidth: "160px", // flexible
    component: ElDatePicker,
    componentProps: {
      style: "width: 100%",
      readonly: true,
      disabled: true,
      format: "DD-MM-YYYY HH:mm:ss",
      type: "datetime",
      valueFormat: "YYYY-MM-DD HH:mm:ss",
    },
  },
  {
    field: "updated_at",
    label: "Updated At",
    inlineEditActive: true,
    minWidth: "160px", // flexible
    component: ElDatePicker,
    componentProps: {
      style: "width: 100%",
      readonly: true,
      disabled: true,
      format: "DD-MM-YYYY HH:mm:ss",
      type: "datetime",
      valueFormat: "YYYY-MM-DD HH:mm:ss",
    },
  },
];
