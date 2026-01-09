
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { ScheduleDTO } from "~/api/types/school.dto";

/* ================================
 * SCHEDULE MANAGEMENT (Admin)
 * ================================ */

export interface AdminCreateScheduleSlot {
  class_id: string;
  teacher_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  room?: string | null;
  subject_id?: string; // optional
}

export interface AdminUpdateScheduleSlot {
  class_id?: string;
  teacher_id?: string;
  day_of_week?: number;
  start_time?: string;
  end_time?: string;
  room?: string | null;
  subject_id?: string;
}

export interface AdminAssignScheduleSlotSubject {
  /** set to string to assign, null to clear */
  subject_id?: string | null;
}

/**
 * Data for a single schedule slot
 */
export interface AdminScheduleSlotData extends ScheduleDTO {
  class_name: string;
  teacher_name: string;
  subject_label: string;
}

export interface AdminScheduleSlotList {
  items: AdminScheduleSlotData[];
  total: number;
  page: number;
  page_size: number;
}

export type AdminGetScheduleSlotResponse = ApiResponse<AdminScheduleSlotData>;
export type AdminGetScheduleListResponse = ApiResponse<AdminScheduleSlotList>;

/* ================================
 * Teacher select (filtered by assignment)
 * ================================ */

export interface SelectOptionDTO {
  value: string;
  label: string;
}

export interface AdminTeacherSelectListDTO {
  items: SelectOptionDTO[];
}

/**
 * Query params for:
 * GET /api/admin/schedule/teacher-select
 */
export interface AdminTeacherSelectQuery {
  class_id: string;
  subject_id: string;
}

export type AdminTeacherSelectListResponse =
  ApiResponse<AdminTeacherSelectListDTO>;
