import type {
  AdminCreateClass,
  // AdminUpdateClass,
} from "~/api/admin/class/class.dto";
import type { Field } from "~/components/types/form";
import { ElInput, ElInputNumber, ElSwitch } from "element-plus";
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";
import { ElSelect, ElOption } from "element-plus";
export const classFormSchema: Field<AdminCreateClass>[] = [
  {
    key: "name",
    label: "Class Name",
    component: ElInput,
    formItemProps: {
      required: true,
      prop: "name",
      label: "Class Name",
    },
    componentProps: {
      placeholder: "Class name (e.g. Grade 7A)",
      clearable: true,
    },
  },
  {
    key: "teacher_id",
    label: "Teacher",
    component: TeacherSelect,
    formItemProps: {
      required: false,
      prop: "teacher_id",
      label: "Teacher",
    },
    componentProps: {
      placeholder: "Optional teacher",
      clearable: true,
    },
  },
  {
    key: "max_students",
    label: "Max Students",
    component: ElInputNumber,
    formItemProps: {
      required: false,
      prop: "max_students",
      label: "Max Students",
    },
    componentProps: {
      min: 1,
      max: 100,
      placeholder: "Optional max students",
    },
  },
  {
    key: "subject_ids",
    label: "Subjects",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      required: false,
      prop: "subject_ids",
      label: "Subjects",
    },
    componentProps: {
      multiple: true,
      filterable: true,
      clearable: true,
      placeholder: "Select subjects",
    },
    childComponentProps: {
      options: [],
      valueKey: "value",
      labelKey: "label",
    },
  },
];
// export const classFormSchemaEdit: Field<AdminUpdateClass>[] = [
//   {
//     key: "code",
//     label: "Class Code",
//     formItemProps: { labelWidth: "120px" },
//     component: ElInput,
//     componentProps: { placeholder: "Enter class code", clearable: true },
//   },
//   {
//     key: "name",
//     label: "Class Name",
//     formItemProps: { labelWidth: "120px" },
//     component: ElInput,
//     componentProps: { placeholder: "Enter class name", clearable: true },
//   },
//   {
//     key: "grade",
//     label: "Grade",
//     formItemProps: { labelWidth: "120px" },
//     component: ElInputNumber,
//     componentProps: { min: 1, max: 12, controlsPosition: "right" },
//   },
//   {
//     key: "max_students",
//     label: "Max Students",
//     formItemProps: { labelWidth: "120px" },
//     component: ElInputNumber,
//     componentProps: { min: 1, max: 100, controlsPosition: "right" },
//   },
//   {
//     key: "academic_year",
//     label: "Academic Year",
//     formItemProps: { labelWidth: "120px" },
//     component: ElInput,
//     componentProps: { placeholder: "Enter academic year", clearable: true },
//   },
//   {
//     key: "status",
//     label: "Status",
//     formItemProps: { labelWidth: "120px" },
//     component: ElSwitch,
//   },
// ];
