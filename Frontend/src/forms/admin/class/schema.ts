import type { AdminCreateClass, AdminUpdateClass } from "~/api/admin/class/dto";
import type { Field } from "~/components/types/form";
import { ElInput, ElInputNumber, ElSwitch } from "element-plus";

export const classFormSchema: Field<AdminCreateClass>[] = [
  {
    key: "code",
    label: "Class Code",
    formItemProps: { labelWidth: "120px" },
    component: ElInput,
    componentProps: { placeholder: "Enter class code", clearable: true },
  },
  {
    key: "name",
    label: "Class Name",
    formItemProps: { labelWidth: "120px" },
    component: ElInput,
    componentProps: { placeholder: "Enter class name", clearable: true },
  },
  {
    key: "grade",
    label: "Grade",
    formItemProps: { labelWidth: "120px" },
    component: ElInputNumber,
    componentProps: { min: 1, max: 12, controlsPosition: "right" },
  },
  {
    key: "max_students",
    label: "Max Students",
    formItemProps: { labelWidth: "120px" },
    component: ElInputNumber,
    componentProps: { min: 1, max: 100, controlsPosition: "right" },
  },
  {
    key: "academic_year",
    label: "Academic Year",
    formItemProps: { labelWidth: "120px" },
    component: ElInput,
    componentProps: { placeholder: "Enter academic year", clearable: true },
  },
  {
    key: "status",
    label: "Status",
    formItemProps: { labelWidth: "120px" },
    component: ElSwitch,
  },
];

export const classFormSchemaEdit: Field<AdminUpdateClass>[] = [
  {
    key: "code",
    label: "Class Code",
    formItemProps: { labelWidth: "120px" },
    component: ElInput,
    componentProps: { placeholder: "Enter class code", clearable: true },
  },
  {
    key: "name",
    label: "Class Name",
    formItemProps: { labelWidth: "120px" },
    component: ElInput,
    componentProps: { placeholder: "Enter class name", clearable: true },
  },
  {
    key: "grade",
    label: "Grade",
    formItemProps: { labelWidth: "120px" },
    component: ElInputNumber,
    componentProps: { min: 1, max: 12, controlsPosition: "right" },
  },
  {
    key: "max_students",
    label: "Max Students",
    formItemProps: { labelWidth: "120px" },
    component: ElInputNumber,
    componentProps: { min: 1, max: 100, controlsPosition: "right" },
  },
  {
    key: "academic_year",
    label: "Academic Year",
    formItemProps: { labelWidth: "120px" },
    component: ElInput,
    componentProps: { placeholder: "Enter academic year", clearable: true },
  },
  {
    key: "status",
    label: "Status",
    formItemProps: { labelWidth: "120px" },
    component: ElSwitch,
  },
];
