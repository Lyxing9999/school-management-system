// ~/api/admin/subject/dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { SubjectDTO } from "~/api/types/school.dto";
/* ================================
 * SUBJECT MANAGEMENT (Admin)
 * ================================ */

/**
 * Payload for creating a subject
 * Python: AdminCreateSubjectSchema
 */
export interface AdminCreateSubjectDTO {
  name: string;
  code: string;
  description?: string | null;
  allowed_grade_levels?: number[] | null;
}

export interface AdminSubjectDataDTO extends SubjectDTO {}
/**
 * List wrapper
 * Python: AdminSubjectListDTO
 */
export interface AdminSubjectListDTO {
  items: AdminSubjectDataDTO[];
}

/**
 * Wrapped responses
 */
export type AdminGetSubjectResponse = ApiResponse<AdminSubjectDataDTO>;
export type AdminGetSubjectListResponse = ApiResponse<AdminSubjectListDTO>;
