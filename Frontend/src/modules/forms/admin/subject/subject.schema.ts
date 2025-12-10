// src/modules/forms/admin/subject/subject.schema.ts
import type { Field } from "~/components/types/form";
import type { AdminCreateSubject } from "~/api/admin/subject/subject.dto";
import { ref } from "vue";
import { ElInput, ElSelect, ElOption } from "element-plus";

export const gradeOptions = ref(
  Array.from({ length: 12 }, (_, i) => ({
    value: i + 1,
    label: `Grade ${i + 1}`,
  }))
);

export const subjectFormFields: Field<AdminCreateSubject>[] = [
  {
    key: "name",
    label: "Name",
    component: ElInput,
    formItemProps: {
      prop: "name",
      label: "Name",
      rules: [
        {
          required: true,
          message: "Name is required",
          trigger: ["blur", "change"],
        },
      ],
    },
    componentProps: {
      placeholder: "Subject name (e.g. Mathematics)",
      clearable: true,
    },
  },
  {
    key: "code",
    label: "Code",
    component: ElInput,
    formItemProps: {
      prop: "code",
      label: "Code",
      rules: [
        {
          required: true,
          message: "Code is required",
          trigger: ["blur", "change"],
        },
      ],
    },
    componentProps: {
      placeholder: "Unique subject code (e.g. MATH101)",
      clearable: true,
    },
  },
  {
    key: "description",
    label: "Description",
    component: ElInput,
    formItemProps: {
      prop: "description",
      label: "Description",
    },
    componentProps: {
      type: "textarea",
      placeholder: "Short description",
      rows: 3,
    },
  },
  {
    key: "allowed_grade_levels",
    label: "Allowed Grade Levels",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      prop: "allowed_grade_levels",
      label: "Allowed Grade Levels",
    },
    componentProps: {
      multiple: true,
      filterable: true,
      clearable: true,
      placeholder: "Select grade levels",
    },
    childComponentProps: {
      options: () => gradeOptions.value,
      valueKey: "value",
      labelKey: "label",
    },
  },
];
