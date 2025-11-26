// ~/api/admin/class/dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { ClassSectionDTO } from "~/api/types/school.dto";

/* ================================
 * CLASS MANAGEMENT (Admin)
 * ================================ */

/**
 * Payload for creating a class
 * Python: AdminCreateClassSchema
 */
export interface AdminCreateClassDTO {
  name: string;
  teacher_id?: string | null;
  subject_ids?: string[] | null;
  max_students?: number | null;
}

export interface AdminClassDataDTO extends ClassSectionDTO {}
/**
 * List wrapper
 * Python: AdminClassListDTO
 */
export interface AdminClassListDTO {
  items: AdminClassDataDTO[];
}

/**
 * Wrapped responses
 */
export type AdminGetClassResponse = ApiResponse<AdminClassDataDTO>;
export type AdminGetClassListResponse = ApiResponse<AdminClassListDTO>;
