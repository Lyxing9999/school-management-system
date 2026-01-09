// ~/api/admin/class/dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { ClassSectionDTO } from "~/api/types/school.dto";
import type { AdminStudentNameSelectDTO } from "~/api/admin/student/student.dto";

/* ================================
 * CLASS MANAGEMENT (Admin)
 * ================================ */

/**
 * Payload for creating a class
 * Python: AdminCreateClassSchema
 */
export interface AdminCreateClass {
  name: string;
  homeroom_teacher_id?: string | null;
  subject_ids?: string[] | null;
  max_students?: number | null;
}

export interface AdminClassNameSelectDTO {
  value: string;
  lable: string;
}
export interface AdminStudentsInClassSelectDTO {
  items: AdminStudentNameSelectDTO[];
}
export interface AdminClassDataDTO extends ClassSectionDTO {
  // enriched fields from backend
  homeroom_teacher_name?: string | null;
  subject_labels?: string[];
  enrolled_count?: number;
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
export type AdminUpdateClassRelationsDTO = {
  student_ids: string[];
  homeroom_teacher_id: string | null;
};

export type AdminUpdateClassRelationsResultDTO = {
  class_id: string;
  homeroom_teacher_changed: boolean;
  homeroom_teacher_id: string | null;
  enrolled_count: number;
  added: string[];
  removed: string[];
  conflicts: Array<{
    student_id: string;
    reason: "ALREADY_ENROLLED" | "NOT_FOUND";
    current_class_id?: string | null;
  }>;
  capacity_rejected: string[];
};

export type SearchStudentsParams = {
  q: string;
  limit?: number;
  cursor?: string | null;
};

export type PagedResult<T> = {
  items: T[];
  nextCursor?: string | null;
};
export type AdminStudentSelectDTO = {
  value: string; // student_id (ObjectId as string)
  label: string; // e.g. "Sok Dara (G10-A) - STU00012"
  // optional extras (only if useful)
  meta?: Record<string, any> | null;
};
export type AdminStudentSelectPagedResultDTO =
  PagedResult<AdminStudentSelectDTO>;
export interface AdminClassPaginatedDTO {
  items: AdminClassDataDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
export type AdminSubjectSelectDTO = {
  value: string; // subject_id
  label: string; // "Name (CODE)"
};

export type AdminSubjectSelectListDTO = {
  items: AdminSubjectSelectDTO[];
};

// query params for server-side list
export type ListClassesParams = {
  q?: string;
  page?: number;
  limit?: number; // maps to backend page_size
  include_deleted?: boolean;
  deleted_only?: boolean;
};
/**
 * Wrapped responses
 */
export type AdminGetClassResponse = ApiResponse<AdminClassDataDTO>;
export type AdminGetClassListResponse = ApiResponse<AdminClassListDTO>;

export type AdminClassNameSelectListResponse =
  ApiResponse<AdminClassNameSelectListDTO>;

export type AdminStudentsInClassSelectResponse =
  ApiResponse<AdminStudentsInClassSelectDTO>;

export type AdminUpdateClassRelationsResponse =
  ApiResponse<AdminUpdateClassRelationsResultDTO>;

export type AdminStudentSelectPagedResultResponse =
  ApiResponse<AdminStudentSelectPagedResultDTO>;
export type AdminGetClassPaginatedResponse =
  ApiResponse<AdminClassPaginatedDTO>;

export type AdminSubjectSelectListResponse =
  ApiResponse<AdminSubjectSelectListDTO>;
