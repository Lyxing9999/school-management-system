// ~/api/admin/schedule/dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { ScheduleDTO } from "~/api/types/school.dto";
/* ================================
 * SCHEDULE MANAGEMENT (Admin)
 * ================================ */

/**
 * Payload for creating a schedule slot
 * (Inferred from ScheduleSlot + AdminScheduleSlotDataDTO)
 *
 * Expected fields:
 * - class_id: str
 * - teacher_id: str
 * - day_of_week: int
 * - start_time: time / string
 * - end_time: time / string
 * - room: Optional[str]
 */
export interface AdminCreateScheduleSlotDTO {
  class_id: string;
  teacher_id: string;
  day_of_week: number; // 0–6 or 1–7 depending on backend convention
  start_time: string; // e.g. "09:00" or ISO time
  end_time: string; // same format as start_time
  room?: string | null;
}

/**
 * Payload for updating a schedule slot
 * (PATCH /api/admin/schedule/slots/:slot_id)
 */
export interface AdminUpdateScheduleSlotDTO {
  class_id?: string;
  teacher_id?: string;
  day_of_week?: number;
  start_time?: string;
  end_time?: string;
  room?: string | null;
}

/**
 * Data for a single schedule slot
 * Python: AdminScheduleSlotDataDTO
 *
 * From SchoolAdminMapper.schedule_slot_to_dto / schedule_slot_doc_to_dto:
 * - id: str
 * - class_id: str
 * - teacher_id: str
 * - day_of_week: int
 * - start_time: time / string
 * - end_time: time / string
 * - room: Optional[str]
 * - created_at: datetime
 * - updated_at: datetime
 */
export interface AdminScheduleSlotDataDTO extends ScheduleDTO {}

/**
 * List wrapper
 * Python: AdminScheduleListDTO
 */
export interface AdminScheduleListDTO {
  items: AdminScheduleSlotDataDTO[];
}

/**
 * Wrapped responses
 */
export type AdminGetScheduleSlotResponse =
  ApiResponse<AdminScheduleSlotDataDTO>;
export type AdminGetScheduleListResponse = ApiResponse<AdminScheduleListDTO>;
