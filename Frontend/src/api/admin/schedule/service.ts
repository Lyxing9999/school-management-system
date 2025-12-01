// ~/api/schedule-slot/service.ts
import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import type {
  AdminCreateScheduleSlotDTO,
  AdminScheduleSlotDataDTO,
  AdminUpdateScheduleSlotDTO,
} from "./dto";
import { ScheduleSlotApi } from "./api";

export class ScheduleSlotService {
  private callApi = useApiUtils().callApi;

  constructor(private scheduleSlotApi: ScheduleSlotApi) {}

  // ============
  // QUERY METHODS
  // ============

  async getClassSchedule(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminScheduleSlotDataDTO>(
      () => this.scheduleSlotApi.getClassSchedule(classId),
      options
    );
    return data!;
  }

  async getTeacherSchedule(teacherId: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminScheduleSlotDataDTO>(
      () => this.scheduleSlotApi.getTeacherSchedule(teacherId),
      options
    );
    return data!;
  }
  async getScheduleSlotById(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminScheduleSlotDataDTO>(
      () => this.scheduleSlotApi.getScheduleSlotById(id),
      options
    );
    return data!;
  }
  // ============
  // COMMANDS
  // ============

  async createScheduleSlot(
    payload: AdminCreateScheduleSlotDTO,
    options?: ApiCallOptions
  ) {
    const scheduleSlotData = await this.callApi<AdminScheduleSlotDataDTO>(
      () => this.scheduleSlotApi.createScheduleSlot(payload),
      { showSuccess: true, ...(options ?? {}) }
    );
    return scheduleSlotData!;
  }

  async updateScheduleSlot(
    slotId: string,
    payload: AdminUpdateScheduleSlotDTO,
    options?: ApiCallOptions
  ) {
    const scheduleSlotData = await this.callApi<AdminScheduleSlotDataDTO>(
      () => this.scheduleSlotApi.updateScheduleSlot(slotId, payload),
      { showSuccess: true, ...(options ?? {}) }
    );
    return scheduleSlotData!;
  }

  async deleteScheduleSlot(slotId: string, options?: ApiCallOptions) {
    const scheduleSlotData = await this.callApi<AdminScheduleSlotDataDTO>(
      () => this.scheduleSlotApi.deleteScheduleSlot(slotId),
      { showSuccess: true, ...(options ?? {}) }
    );
    return scheduleSlotData!;
  }
}
