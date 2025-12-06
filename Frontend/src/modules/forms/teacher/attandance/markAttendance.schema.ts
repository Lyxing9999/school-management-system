import { computed, type Ref, type ComputedRef } from "vue";
import type { Field } from "~/components/types/form";
import type { TeacherMarkAttendanceForm } from "../types";
import TeacherClassStudentSelect from "~/components/Selects/TeacherClassStudentSelect.vue";
import { ElSelect, ElOption, ElDatePicker } from "element-plus";

export function useAttendanceFormSchema(
  selectedClassId: Ref<string | null>
): ComputedRef<Field<TeacherMarkAttendanceForm>[]> {
  return computed<Field<TeacherMarkAttendanceForm>[]>(() => [
    {
      key: "student_id",
      label: "Student",
      component: TeacherClassStudentSelect,
      componentProps: {
        classId: selectedClassId.value || "",
        reload: true,
        valueKey: "id",
        labelKey: "username",
        multiple: false,
        placeholder: "Select student",
        disabled: !selectedClassId.value,
      },
    },
    {
      key: "status",
      label: "Status",
      component: ElSelect,
      childComponent: ElOption,
      childComponentProps: {
        options: [
          { label: "Present", value: "present" },
          { label: "Absent", value: "absent" },
          { label: "Excused", value: "excused" },
        ],
        labelKey: "label",
        valueKey: "value",
      },
      componentProps: {
        placeholder: "Select status",
        style: "width: 100%",
      },
    },
    {
      key: "record_date",
      label: "Date",
      component: ElDatePicker,
      componentProps: {
        type: "date",
        valueFormat: "YYYY-MM-DD",
        placeholder: "Pick a day",
        style: "width: 100%",
        disabledDate: (date: Date) => {
          const today = new Date();
          today.setHours(0, 0, 0, 0);

          const candidate = new Date(date);
          candidate.setHours(0, 0, 0, 0);

          return candidate.getTime() > today.getTime();
        },
      },
    },
  ]);
}
