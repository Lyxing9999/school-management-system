import type { AxiosInstance } from "axios";
import type {
  AdminCreateScheduleSlotDTO,
  AdminGetScheduleSlotResponse,
  AdminUpdateScheduleSlotDTO,
} from "./dto";

export class ScheduleSlotApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/schedule"
  ) {}

  // ============
  // QUERY
  // ============

  async getClassSchedule(classId: string) {
    const res = await this.$api.get<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/classes/${classId}`
    );
    return res.data;
  }

  async getTeacherSchedule(teacherId: string) {
    const res = await this.$api.get<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/teachers/${teacherId}`
    );
    return res.data;
  }

  async createScheduleSlot(data: AdminCreateScheduleSlotDTO) {
    const res = await this.$api.post<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/slots`,
      data
    );
    return res.data;
  }

  async updateScheduleSlot(slotId: string, data: AdminUpdateScheduleSlotDTO) {
    const res = await this.$api.patch<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/slots/${slotId}`,
      data
    );
    return res.data;
  }

  async deleteScheduleSlot(slotId: string) {
    const res = await this.$api.delete<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/slots/${slotId}`
    );
    return res.data;
  }
}
