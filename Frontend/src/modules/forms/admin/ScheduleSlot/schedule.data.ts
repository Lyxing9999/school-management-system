import { reactive } from "vue";
import type {
  AdminCreateScheduleSlot,
  AdminUpdateScheduleSlot,
} from "~/api/admin/schedule/schedule.dto";

export const getScheduleFormData = (): AdminCreateScheduleSlot => ({
  class_id: "",
  teacher_id: "",
  day_of_week: 1,
  start_time: "08:00",
  end_time: "09:00",
  room: "",
});

export const getScheduleFormDataEdit = (
  data?: Partial<AdminUpdateScheduleSlot>
): AdminUpdateScheduleSlot =>
  reactive({
    day_of_week: 1,
    start_time: "08:00",
    end_time: "09:00",
    room: "",
    ...data,
  });
