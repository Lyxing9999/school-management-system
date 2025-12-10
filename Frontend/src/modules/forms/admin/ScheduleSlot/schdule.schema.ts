import type {
  AdminCreateScheduleSlot,
  AdminUpdateScheduleSlot,
} from "~/api/admin/schedule/schedule.dto";

import type { Field } from "~/components/types/form";
import { ElSelect, ElOption, ElTimeSelect, ElInput } from "element-plus";
import ClassSelect from "~/components/Selects/ClassSelect.vue";
import TeacherSelect from "~/components/Selects/TeacherSelect.vue";
import { dayOptions } from "~/utils/constants/dayOptions";

export const scheduleFormSchema: Field<AdminCreateScheduleSlot>[] = [
  {
    key: "class_id",
    label: "Class",
    component: ClassSelect,
    formItemProps: {
      required: true,
      prop: "class_id",
      label: "Class",
    },
    componentProps: {
      placeholder: "Select class",
      filterable: true,
      clearable: false,
      format: "HH:mm",
    },
  },
  {
    key: "teacher_id",
    label: "Teacher",
    component: TeacherSelect,
    formItemProps: {
      required: true,
      prop: "teacher_id",
      label: "Teacher",
    },
    componentProps: {
      placeholder: "Select teacher",
      clearable: true,
    },
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
    componentProps: {
      step: "00:15",
      placeholder: "Select day",
    },
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
    formItemProps: {
      required: true,
      prop: "start_time",
      label: "Start Time",
    },
    componentProps: {
      step: "00:15",
      placeholder: "Select start time",
      format: "HH:mm",
    },
  },
  {
    key: "end_time",
    label: "End Time",
    component: ElTimeSelect,
    formItemProps: {
      required: true,
      prop: "end_time",
      label: "End Time",
    },
    componentProps: {
      placeholder: "Select end time",
      format: "HH:mm",
    },
  },
  {
    key: "room",
    label: "Room",
    component: ElInput,
    formItemProps: {
      required: false,
      prop: "room",
      label: "Room",
    },
    componentProps: {
      placeholder: "Room (optional)",
      clearable: true,
    },
  },
];

export const scheduleFormSchemaEdit: Field<AdminUpdateScheduleSlot>[] = [
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
    componentProps: {
      placeholder: "Select day",
    },
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
    formItemProps: {
      required: true,
      prop: "start_time",
      label: "Start Time",
    },
    componentProps: {
      start: "07:00",
      step: "00:15",
      end: "18:00",
      placeholder: "Start time",
      format: "HH:mm",
    },
  },
  {
    key: "end_time",
    label: "End Time",
    component: ElTimeSelect,
    formItemProps: {
      required: true,
      prop: "end_time",
      label: "End Time",
    },
    componentProps: {
      start: "07:00",
      step: "00:15",
      end: "18:00",
      placeholder: "End time",
      format: "HH:mm",
    },
  },
  {
    key: "room",
    label: "Room",
    component: ElInput,
    formItemProps: {
      required: false,
      prop: "room",
      label: "Room",
    },
    componentProps: {
      placeholder: "Room (optional)",
      clearable: true,
    },
  },
];
