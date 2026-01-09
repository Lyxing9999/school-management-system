
import type { AxiosInstance } from "axios";
import type {
  AdminCreateScheduleSlot,
  AdminAssignScheduleSlotSubject,
  AdminGetScheduleSlotResponse,
  AdminUpdateScheduleSlot,
  AdminGetScheduleListResponse,
  AdminTeacherSelectListResponse,
  AdminTeacherSelectQuery,
} from "./schedule.dto";

export class ScheduleSlotApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/schedule"
  ) {}

  // ============
  // QUERY
  // ============

  async getScheduleSlotById(id: string) {
    const res = await this.$api.get<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/slots/${id}`
    );
    return res.data;
  }

  async getClassSchedule(
    classId: string,
    params?: { page?: number; page_size?: number }
  ) {
    const res = await this.$api.get<AdminGetScheduleListResponse>(
      `${this.baseURL}/classes/${classId}`,
      { params }
    );
    return res.data;
  }

  async getTeacherSchedule(
    teacherId: string,
    params?: { page?: number; page_size?: number }
  ) {
    const res = await this.$api.get<AdminGetScheduleListResponse>(
      `${this.baseURL}/teachers/${teacherId}`,
      { params }
    );
    return res.data;
  }

  /**
   * Teacher select options filtered by assignment (teacher_subject_assignments)
   *
   * Expected backend:
   * GET /api/admin/schedule/teacher-select?class_id=...&subject_id=...
   *
   * Returns:
   * { success, message, data: { items: [{ value, label }] } }
   */
  async listTeacherSelectByAssignment(params: AdminTeacherSelectQuery) {
    const res = await this.$api.get<AdminTeacherSelectListResponse>(
      `${this.baseURL}/teacher-select`,
      { params }
    );
    return res.data;
  }

  // ============
  // COMMAND
  // ============

  async createScheduleSlot(data: AdminCreateScheduleSlot) {
    const res = await this.$api.post<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/slots`,
      data
    );
    return res.data;
  }

  async updateScheduleSlot(slotId: string, data: AdminUpdateScheduleSlot) {
    const res = await this.$api.patch<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/slots/${slotId}`,
      data
    );
    return res.data;
  }

  async updateScheduleSlotSubject(
    slotId: string,
    data: AdminAssignScheduleSlotSubject
  ) {
    const res = await this.$api.patch<AdminGetScheduleSlotResponse>(
      `${this.baseURL}/slots/${slotId}/subject`,
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
