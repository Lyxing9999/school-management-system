// ~/modules/forms/admin/teachingAssignmentForm.ts
import type { Field } from "~/components/types/form";
import { ElSwitch } from "element-plus";

import TeacherSelect from "~/components/selects/teacher/TeacherSelect.vue";
import ClassSubjectSelect from "~/components/selects/composite/ClassSubjectSelect.vue";

/**
 * For SmartFormDialog model (assign / edit)
 */
export type AdminAssignTeachingAssignmentForm = {
  class_id: string; // locked by page selection
  subject_id: string;
  teacher_id: string;
  overwrite: boolean;
};

export const teachingAssignmentFormSchema: Field<AdminAssignTeachingAssignmentForm>[] =
  [
    {
      key: "subject_id",
      label: "Subject",
      component: ClassSubjectSelect,
      formItemProps: { required: true, prop: "subject_id", label: "Subject" },
      componentProps: (model) => ({
        classId: model.class_id || "",
        placeholder: "Select subject",
        clearable: true,
        disabled: !model.class_id,
      }),
    },
    {
      key: "teacher_id",
      label: "Teacher",
      component: TeacherSelect,
      formItemProps: { required: true, prop: "teacher_id", label: "Teacher" },
      componentProps: {
        placeholder: "Select teacher",
        clearable: true,
      },
    },
    {
      key: "overwrite",
      label: "Overwrite",
      component: ElSwitch,
      formItemProps: { required: false, prop: "overwrite", label: "Overwrite" },
      componentProps: {
        activeText: "Replace existing teacher",
        inactiveText: "Block if already assigned",
      },
    },
  ];
