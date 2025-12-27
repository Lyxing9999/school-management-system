// ~/tables/columns/admin/scheduleColumns.ts
import { h, type ComputedRef } from "vue";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { AdminScheduleSlotData } from "~/api/admin/schedule/schedule.dto";

const dayOfWeekLabels = ["", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function createScheduleColumns(
  teacherLabelMap: ComputedRef<Record<string, string>>
): ColumnConfig<AdminScheduleSlotData>[] {
  return [
    {
      label: "Day",
      field: "day_of_week",
      align: "center",
      width: "80px",
      render: (row: AdminScheduleSlotData) =>
        h("span", dayOfWeekLabels[row.day_of_week] ?? row.day_of_week),
    },
    {
      label: "Time",
      field: "start_time",
      align: "center",
      minWidth: "160px",
      render: (row: AdminScheduleSlotData) =>
        h(
          "span",
          `${row.start_time?.slice(0, 5)} - ${row.end_time?.slice(0, 5)}`
        ),
    },
    {
      label: "Room",
      field: "room",
      align: "center",
      minWidth: "100px",
    },
    {
      label: "Class",
      field: "class_name",
      align: "left",
      minWidth: "160px",
      render: (row: AdminScheduleSlotData) => h("span", row.class_name),
    },
    {
      label: "Teacher",
      field: "teacher_name",
      align: "left",
      minWidth: "180px",
      render: (row: AdminScheduleSlotData) =>
        h(
          "span",
          row.teacher_name ||
            teacherLabelMap.value[row.teacher_id] ||
            row.teacher_id
        ),
    },
    {
      field: "id",
      operation: true,
      label: "Operation",
      inlineEditActive: false,
      align: "center",
      minWidth: "200px",
      smartProps: {},
    },
  ];
}
