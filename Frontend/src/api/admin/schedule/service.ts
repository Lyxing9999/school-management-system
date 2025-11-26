import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminCreateScheduleSlotDTO,
  AdminScheduleSlotDataDTO,
  AdminUpdateScheduleSlotDTO,
} from "./dto";
import { ScheduleSlotApi } from "./api";

export class ScheduleSlotService {
  private safeApiCall = useApiUtils().safeApiCall;

  constructor(private scheduleSlotApi: ScheduleSlotApi) {}

  // ============
  // QUERY METHODS
  // ============
  async getClassSchedule(classId: string) {
    const { data } = await this.safeApiCall<AdminScheduleSlotDataDTO>(() =>
      this.scheduleSlotApi.getClassSchedule(classId)
    );
    return data!;
  }

  async getTeacherSchedule(teacherId: string) {
    const { data } = await this.safeApiCall<AdminScheduleSlotDataDTO>(() =>
      this.scheduleSlotApi.getTeacherSchedule(teacherId)
    );
    return data!;
  }
  async createScheduleSlot(data: AdminCreateScheduleSlotDTO) {
    const { data: scheduleSlotData } =
      await this.safeApiCall<AdminScheduleSlotDataDTO>(() =>
        this.scheduleSlotApi.createScheduleSlot(data)
      );
    return scheduleSlotData!;
  }
  async updateScheduleSlot(slotId: string, data: AdminUpdateScheduleSlotDTO) {
    const { data: scheduleSlotData } =
      await this.safeApiCall<AdminScheduleSlotDataDTO>(() =>
        this.scheduleSlotApi.updateScheduleSlot(slotId, data)
      );
    return scheduleSlotData!;
  }
  async deleteScheduleSlot(slotId: string) {
    const { data: scheduleSlotData } =
      await this.safeApiCall<AdminScheduleSlotDataDTO>(() =>
        this.scheduleSlotApi.deleteScheduleSlot(slotId)
      );
    return scheduleSlotData!;
  }
}
