// ~/api/schedule-slot/service.ts
import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";
import type {
  AdminCreateScheduleSlot,
  AdminAssignScheduleSlotSubject,
  AdminScheduleSlotData,
  AdminUpdateScheduleSlot,
  AdminScheduleSlotList,
} from "./schedule.dto";
import { ScheduleSlotApi } from "./schedule.api";

type ScheduleListParams = { page?: number; page_size?: number };

export class ScheduleSlotService {
  private callApi = useApiUtils().callApi;

  constructor(private scheduleSlotApi: ScheduleSlotApi) {}

  // ============
  // QUERY METHODS
  // ============

  async getClassSchedule(
    classId: string,
    params?: ScheduleListParams,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminScheduleSlotList>(
      () => this.scheduleSlotApi.getClassSchedule(classId, params),
      options
    );
    return data!;
  }

  async getTeacherSchedule(
    teacherId: string,
    params?: ScheduleListParams,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminScheduleSlotList>(
      () => this.scheduleSlotApi.getTeacherSchedule(teacherId, params),
      options
    );
    return data!;
  }

  async getScheduleSlotById(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminScheduleSlotData>(
      () => this.scheduleSlotApi.getScheduleSlotById(id),
      options
    );
    return data!;
  }

  // ============
  // COMMANDS
  // ============

  async createScheduleSlot(
    payload: AdminCreateScheduleSlot,
    options?: ApiCallOptions
  ) {
    const scheduleSlotData = await this.callApi<AdminScheduleSlotData>(
      () => this.scheduleSlotApi.createScheduleSlot(payload),
      { showSuccess: true, ...(options ?? {}) }
    );
    return scheduleSlotData!;
  }

  async updateScheduleSlot(
    slotId: string,
    payload: AdminUpdateScheduleSlot,
    options?: ApiCallOptions
  ) {
    const scheduleSlotData = await this.callApi<AdminScheduleSlotData>(
      () => this.scheduleSlotApi.updateScheduleSlot(slotId, payload),
      { showSuccess: true, ...(options ?? {}) }
    );
    return scheduleSlotData!;
  }

  async updateScheduleSlotSubject(
    slotId: string,
    payload: AdminAssignScheduleSlotSubject,
    options?: ApiCallOptions
  ) {
    const scheduleSlotData = await this.callApi<AdminScheduleSlotData>(
      () => this.scheduleSlotApi.updateScheduleSlotSubject(slotId, payload),
      { showSuccess: true, ...(options ?? {}) }
    );
    return scheduleSlotData!;
  }

  async deleteScheduleSlot(slotId: string, options?: ApiCallOptions) {
    const scheduleSlotData = await this.callApi<AdminScheduleSlotData>(
      () => this.scheduleSlotApi.deleteScheduleSlot(slotId),
      { showSuccess: true, ...(options ?? {}) }
    );
    return scheduleSlotData!;
  }
}
