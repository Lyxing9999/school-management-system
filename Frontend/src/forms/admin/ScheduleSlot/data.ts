import { reactive } from "vue";
import type {
  AdminCreateScheduleSlotDTO,
  AdminUpdateScheduleSlotDTO,
} from "~/api/admin/schedule/dto";

export const getScheduleFormData = (): AdminCreateScheduleSlotDTO => ({
  class_id: "",
  teacher_id: "",
    day_of_week: 1,
    start_time: "08:00",
  end_time: "09:00",
  room: "",
});

export const getScheduleFormDataEdit = (
  data?: Partial<AdminUpdateScheduleSlotDTO>
): AdminUpdateScheduleSlotDTO =>
  reactive({
    day_of_week: 1,
    start_time: "08:00",
    end_time: "09:00",
    room: "",
    ...data,
  });
