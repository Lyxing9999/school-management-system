import type {
  AdminCreateScheduleSlot,
  AdminUpdateScheduleSlot,
} from "~/api/admin/schedule/schedule.dto";

import type { Field } from "~/components/types/form";
import { ElSelect, ElOption, ElTimeSelect, ElInput } from "element-plus";
import ClassSelect from "~/components/selects/class/ClassSelect.vue";
import TeacherSelectByAssignment from "~/components/selects/teacher/TeacherSelectByAssignment.vue";
import { dayOptions } from "~/utils/constants/dayOptions";

import ClassSubjectSelect from "~/components/selects/composite/ClassSubjectSelect.vue";

export const scheduleFormSchema: Field<AdminCreateScheduleSlot>[] = [
  {
    key: "class_id",
    label: "Class",
    component: ClassSelect,
    formItemProps: { required: true, prop: "class_id", label: "Class" },
    componentProps: {
      placeholder: "Select class",
      filterable: true,
      clearable: false,
    },
  },

  {
    key: "subject_id",
    label: "Subject",
    component: ClassSubjectSelect,
    formItemProps: { required: false, prop: "subject_id", label: "Subject" },
    componentProps: (model) => ({
      classId: model.class_id || "",
      placeholder: "Select subject (optional)",
      clearable: true,
      disabled: !model.class_id,
    }),
  },

  {
    key: "teacher_id",
    label: "Teacher",
    component: TeacherSelectByAssignment,
    formItemProps: { required: true, prop: "teacher_id", label: "Teacher" },
    componentProps: (model) => ({
      classId: model.class_id || "",
      subjectId: model.subject_id || null,
      placeholder: model.subject_id
        ? "Select assigned teacher"
        : "Select teacher",
      disabled: !model.class_id,
    }),
  },
  {
    key: "day_of_week",
    label: "Day of Week",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      required: true,
      prop: "day_of_week",
      label: "Day of Week",
    },
    componentProps: { placeholder: "Select day" },
    childComponentProps: {
      options: () => dayOptions,
      valueKey: "value",
      labelKey: "label",
    },
  },
  {
    key: "start_time",
    label: "Start Time",
    component: ElTimeSelect,
    formItemProps: { required: true, prop: "start_time", label: "Start Time" },
    componentProps: {
      start: "06:00",
      end: "22:00",
      step: "00:15",
      placeholder: "Select start time",
      format: "HH:mm",
    },
  },
  {
    key: "end_time",
    label: "End Time",
    component: ElTimeSelect,
    formItemProps: { required: true, prop: "end_time", label: "End Time" },
    componentProps: {
      start: "06:00",
      end: "22:00",
      step: "00:15",
      placeholder: "Select end time",
      format: "HH:mm",
    },
  },
  {
    key: "room",
    label: "Room",
    component: ElInput,
    formItemProps: { required: false, prop: "room", label: "Room" },
    componentProps: { placeholder: "Room (optional)", clearable: true },
  },
];

export const scheduleFormSchemaEdit: Field<AdminUpdateScheduleSlot>[] = [
  {
    key: "subject_id",
    label: "Subject",
    component: ClassSubjectSelect,
    formItemProps: { required: false, prop: "subject_id", label: "Subject" },
    componentProps: (model: any) => ({
      classId: model.class_id || model.classId || "",
      placeholder: "Select subject (optional)",
      clearable: true,
      disabled: !(model.class_id || model.classId),
    }),
  },

  {
    key: "day_of_week",
    label: "Day of Week",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      required: true,
      prop: "day_of_week",
      label: "Day of Week",
    },
    componentProps: { placeholder: "Select day" },
    childComponentProps: {
      options: () => dayOptions,
      valueKey: "value",
      labelKey: "label",
    },
  },
  {
    key: "start_time",
    label: "Start Time",
    component: ElTimeSelect,
    formItemProps: { required: true, prop: "start_time", label: "Start Time" },
    componentProps: {
      start: "06:00",
      step: "00:15",
      end: "22:00",
      placeholder: "Start time",
      format: "HH:mm",
    },
  },
  {
    key: "end_time",
    label: "End Time",
    component: ElTimeSelect,
    formItemProps: { required: true, prop: "end_time", label: "End Time" },
    componentProps: {
      start: "06:00",
      step: "00:15",
      end: "22:00",
      placeholder: "End time",
      format: "HH:mm",
    },
  },
  {
    key: "room",
    label: "Room",
    component: ElInput,
    formItemProps: { required: false, prop: "room", label: "Room" },
    componentProps: { placeholder: "Room (optional)", clearable: true },
  },
];
