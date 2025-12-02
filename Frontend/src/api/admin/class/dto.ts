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

export interface AdminClassNameSelectDTO {
  id: string;
  name: string;
}

export interface AdminClassDataDTO extends ClassSectionDTO {
  // enriched fields from backend
  teacher_name?: string | null;
  subject_labels?: string[];

  // convenience counts from backend
  student_count?: number;
  subject_count?: number;
}

/**
 * List wrapper
 * Python: AdminClassListDTO
 */
export interface AdminClassListDTO {
  items: AdminClassDataDTO[];
}
/**
 * List wrapper
 * Python: AdminClassListDTO
 */
export interface AdminClassNameSelectListDTO {
  items: AdminClassNameSelectDTO[];
}
/**
 * Wrapped responses
 */
export type AdminGetClassResponse = ApiResponse<AdminClassDataDTO>;
export type AdminGetClassListResponse = ApiResponse<AdminClassListDTO>;

export type AdminClassNameSelectListResponse =
  ApiResponse<AdminClassNameSelectListDTO>;
