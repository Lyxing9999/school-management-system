import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { SubjectDTO } from "~/api/types/school.dto";

export type SubjectStatus = "all" | "active" | "inactive";

export interface AdminCreateSubject {
  name: string;
  code: string;
  description?: string | null;
  allowed_grade_levels?: number[] | null;
}

export type AdminUpdateSubject = Partial<AdminCreateSubject>;

/**
 * Admin item DTO (matches Python AdminSubjectDataDTO)
 */
export interface AdminSubjectDataDTO extends SubjectDTO {
  // If your backend returns lifecycle in subject docs, keep this.
  // If not returned yet, you can remove it or keep optional.
  lifecycle?: {
    created_at?: string | null;
    updated_at?: string | null;
    deleted_at?: string | null;
    deleted_by?: string | null;
  } | null;
}

/**
 * Paginated wrapper (matches Python AdminSubjectPaginatedDTO)
 */
export interface AdminSubjectPaginatedDTO {
  items: AdminSubjectDataDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AdminSubjectNameSelectDTO {
  items: { id: string; name: string }[];
}
/**
 * Wrapped responses
 */
export type AdminGetSubjectResponse = ApiResponse<AdminSubjectDataDTO>;
export type AdminSubjectPaginatedListResponse =
  ApiResponse<AdminSubjectPaginatedDTO>;
export type AdminSubjectNameSelectListResponse =
  ApiResponse<AdminSubjectNameSelectDTO>;
