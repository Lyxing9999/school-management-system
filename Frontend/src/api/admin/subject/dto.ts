import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { SubjectBaseDataDTO } from "~/api/types/subject.dto";

export interface AdminGetSubjectsData extends SubjectBaseDataDTO {}

export interface AdminCreateSubject {
  name: string;
  teacher_id: string[];
}

export interface AdminUpdateSubject {
  name?: string;
  teacher_id?: string[];
}
export interface AdminGetSubject extends SubjectBaseDataDTO {}

export type AdminSubjectResponse = ApiResponse<AdminGetSubjectsData>;
