import type { AdminCreateClass } from "~/api/admin/admin.dto";
import type { Field } from "~/components/types/form";
import { ElInput, ElInputNumber, ElSwitch } from "element-plus";
export const classFormData: AdminCreateClass = {
  code: "",
  name: "",
  grade: 1,
  max_students: 30,
  academic_year: "",
  status: true,
};

export const classFormSchema: Field<AdminCreateClass>[] = [
  {
    key: "code",
    label: "Class Code",
    labelWidth: "120px",
    component: ElInput,
    componentProps: { placeholder: "Enter class code", clearable: true },
  },
  {
    key: "name",
    label: "Class Name",
    labelWidth: "120px",
    component: ElInput,
    componentProps: { placeholder: "Enter class name", clearable: true },
  },
  {
    key: "grade",
    label: "Grade",
    labelWidth: "120px",
    component: ElInputNumber,
    componentProps: { min: 1, max: 12, controlsPosition: "right" },
  },
  {
    key: "max_students",
    label: "Max Students",
    labelWidth: "120px",
    component: ElInputNumber,
    componentProps: { min: 1, max: 100, controlsPosition: "right" },
  },
  {
    key: "academic_year",
    label: "Academic Year",
    labelWidth: "120px",
    component: ElInput,
    componentProps: { placeholder: "Enter academic year", clearable: true },
  },
  {
    key: "status",
    label: "Status",
    labelWidth: "120px",
    component: ElSwitch,
  },
];
