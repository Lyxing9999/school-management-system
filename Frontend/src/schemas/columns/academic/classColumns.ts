import {
  ElInputNumber,
  ElSwitch,
  ElSelect,
  ElOption,
  ElInput,
} from "element-plus";

const allStudents = ref<string[]>([]);
import type { AcademicBaseClassDataDTO } from "~/api/academic/academic.dto";
import type { ColumnConfig } from "~/components/types/tableEdit";


export const classColumns: ColumnConfig<AcademicBaseClassDataDTO>[] = [
  {
    field: "name",
    label: "Name",
    width: "200px",

    autoSave: true,
    controls: false,
  },
  {
    field: "grade",
    label: "Grade",
    width: "150px",
    align: "center",
    autoSave: true,
    customClass: "flex justify-center items-center cursor-pointer",
    component: ElInputNumber,
    controls: false,
    componentProps: {
      size: "small",
    },
  },
  {
    field: "max_students",
    label: "Max Students",
    autoSave: true,
    width: "150px",
    align: "center",
    customClass: "flex justify-center items-center cursor-pointer",
    controls: false,
    component: ElInputNumber,
    componentProps: {
      size: "small",
    },
  },
  {
    field: "status",
    label: "Status",
    width: "100px",
    align: "center",
    customClass: "flex justify-center items-center cursor-pointer",
    component: ElSwitch,
    inlineEditActive: true,
  },
  {
    field: "homeroom_teacher",
    label: "Homeroom Teacher",
    width: "200px",
  },
  {
    field: "students",
    label: "Students",
    width: "250px",
    inlineEditActive: false,
    component: ElSelect,
    controls: false,
    autoSave: true,
    componentProps: {
      multiple: true,
      filterable: true,
      allowCreate: true,
      collapseTags: true,
      placeholder: "Select students",
    },
    childComponent: ElOption,
    childComponentProps: {
      slots: {
        footer: () => h("span", "Footer"),
      },
      options: allStudents.value.map((s) => ({ label: s, value: s })),
      valueKey: "value",
      labelKey: "label",
    },
    footer: true,
  },
  {
    field: "subjects",
    label: "Subjects",
    width: "200px",

    inlineEditActive: false,
    component: ElSelect,
    componentProps: {
      multiple: true,
      filterable: true,
      allowCreate: true,
      collapseTags: true,
      placeholder: "Select subjects",
      onChange: (val: string[], row: any) => {
        row.students = val;
        val.forEach((s) => {
          if (!allStudents.value.includes(s)) allStudents.value.push(s);
        });
      },
    },
    childComponent: ElOption,
    childComponentProps: {
      options: allStudents.value.map((s) => ({ label: s, value: s })),
      valueKey: "value",
      labelKey: "label",
    },
  },
  {
    field: "created_by",
    label: "Created By",
    width: "120px",
    inlineEditActive: true,
    align: "center",
    controls: false,
    render: (row: any) => row.created_by,
  },
  {
    field: "created_at",
    label: "Created At",
    width: "200px",
    inlineEditActive: true,
    controls: false,
    component: ElInput,
    componentProps: {
      readonly: true,
      disabled: true,
    },
  },
  {
    field: "updated_at",
    label: "Updated At",
    width: "200px",
    controls: false,
    inlineEditActive: true,
    component: ElInput,
    componentProps: {
      readonly: true,
      disabled: true,
    },
  },
  {
    operation: true,
    label: "Operation",
    fixed: "right",
    align: "center",
    width: "150px",
  },
];
