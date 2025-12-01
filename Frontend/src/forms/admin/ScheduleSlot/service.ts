import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types/serviceFormTypes";
import type {
  AdminCreateScheduleSlotDTO,
  AdminUpdateScheduleSlotDTO,
} from "~/api/admin/schedule/dto";

export function useServiceFormScheduleSlot(): UseFormService<
  AdminCreateScheduleSlotDTO,
  AdminUpdateScheduleSlotDTO
> {
  const adminApiService = adminService();

  return {
    create: (data) => adminApiService.scheduleSlot.createScheduleSlot(data), // create staff linked by create user
    update: (id, data) =>
      adminApiService.scheduleSlot.updateScheduleSlot(id, data),
    // delete: can be added in the future
    getDetail: (id) => adminApiService.scheduleSlot.getScheduleSlotById(id),
  };
}
