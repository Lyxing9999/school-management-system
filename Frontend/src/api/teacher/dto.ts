// ~/api/teacher/dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type {
  ClassSectionDTO,
  AttendanceDTO,
  GradeDTO,
  AttendanceStatus,
  GradeType,
  ScheduleDTO,
} from "~/api/types/school.dto";

import type { StudentBaseDataDTO } from "../types/student.dto";
export interface PagedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface TeacherStudentDataDTO extends StudentBaseDataDTO {}
export type GradeEnriched = GradeDTO & {
  student_name?: string;
  student_name_en?: string;
  student_name_kh?: string;

  class_name?: string;
  subject_label?: string;
  teacher_name?: string;

  student_id?: string;
  subject_id?: string;
  class_id?: string;
};
/**
 * Python: TeacherStudentNameSelectDTO
 */
export interface TeacherStudentNameSelectDTO {
  id: string;
  name: string;
}

export interface TeacherStudentNameDTO {
  id: string;
  name: string;
}

export interface TeacherStudentNameListDTO {
  items: TeacherStudentNameDTO[];
}

/**
 * Python: TeacherStudentSelectNameListDTO
 */
export interface TeacherStudentSelectNameListDTO {
  items: TeacherStudentNameSelectDTO[];
}

/**
 * Python: TeacherSubjectNameSelectDTO
 */
export interface TeacherSubjectNameSelectDTO {
  id: string;
  name: string;
}

/**
 * Python: TeacherSubjectSelectNameListDTO
 */
export interface TeacherSubjectSelectNameListDTO {
  items: TeacherSubjectNameSelectDTO[];
}

/**
 * Python: TeacherClassSelectNameListDTO
 */
export interface TeacherClassSelectNameListDTO {
  items: TeacherClassListDTO[];
}

/**
 * Python: TeacherClassListDTO
 */
export interface TeacherClassListDTO {
  items: ClassSectionDTO[];
}

/**
 * Python: TeacherAttendanceListDTO
 */
export interface TeacherAttendanceListDTO {
  items: AttendanceDTO[];
}

/**
 * Python: TeacherGradeListDTOPage
 */

export type TeacherGradePagedDTO = PagedResult<GradeEnriched>;

/**
 * Request DTOs
 * mirror app.contexts.teacher.data_transfer.requests.*
 */

export interface TeacherMarkAttendanceDTO {
  student_id: string;
  class_id: string;
  status: AttendanceStatus;
  record_date?: string; // "YYYY-MM-DD"
}

export interface TeacherChangeAttendanceStatusDTO {
  new_status: AttendanceStatus;
}

export interface TeacherAddGradeDTO {
  student_id: string;
  subject_id: string;
  class_id?: string | null;
  score: number;
  type: GradeType;
  term?: string | null;
}

export interface TeacherUpdateGradeScoreDTO {
  score: number;
}

export interface TeacherChangeGradeTypeDTO {
  type: GradeType;
}

export interface TeacherScheduleDTO extends ScheduleDTO {
  class_name?: string;
  subject_id?: string;
  subject_label?: string;
  teacher_name?: string;

  day_label?: string;
}
export interface TeacherScheduleListDTO {
  items: TeacherScheduleDTO[];
  total: number;
  page: number;
  page_size: number;
}

export interface TeacherClassSummaryDTO {
  total_classes: number;
  total_students: number;
  total_subjects: number;
}

export interface TeacherClassListWithSummeryDTO {
  items: ClassSectionDTO[];
  summary: TeacherClassSummaryDTO;
}

/**
 * Wrapped responses
 */
export type TeacherGetClassesResponse = ApiResponse<TeacherClassListDTO>;
export type TeacherMarkAttendanceResponse = ApiResponse<AttendanceDTO>;
export type TeacherChangeAttendanceStatusResponse = ApiResponse<AttendanceDTO>;
export type TeacherAddGradeResponse = ApiResponse<GradeDTO>;
export type TeacherUpdateGradeScoreResponse = ApiResponse<GradeDTO>;
export type TeacherChangeGradeTypeResponse = ApiResponse<GradeDTO>;
export type TeacherListClassAttendanceResponse =
  ApiResponse<TeacherAttendanceListDTO>;
export type TeacherListClassGradesResponse = ApiResponse<TeacherGradePagedDTO>;

export type TeacherSubjectsSelectNameListResponse =
  ApiResponse<TeacherSubjectSelectNameListDTO>;
export type TeacherStudentsSelectNameListResponse =
  ApiResponse<TeacherStudentSelectNameListDTO>;

export type TeacherClassSelectNameListResponse =
  ApiResponse<TeacherClassSelectNameListDTO>;

export type TeacherStudentNameListResponse =
  ApiResponse<TeacherStudentNameListDTO>;

export type TeacherListMyScheduleResponse = ApiResponse<TeacherScheduleListDTO>;

export type TeacherClassListWithSummeryResponse =
  ApiResponse<TeacherClassListWithSummeryDTO>;

export type TeacherStudentDataResponse = ApiResponse<TeacherStudentDataDTO>;

// ---------- Mutations: soft delete / restore ----------

export interface TeacherSoftDeleteResultDTO {
  modified_count: number;
  deleted: boolean;
}

export interface TeacherRestoreResultDTO {
  modified_count: number;
  restored: boolean;
}

// Wrapped responses
export type TeacherSoftDeleteGradeResponse =
  ApiResponse<TeacherSoftDeleteResultDTO>;
export type TeacherRestoreGradeResponse = ApiResponse<TeacherRestoreResultDTO>;

export type TeacherSoftDeleteAttendanceResponse =
  ApiResponse<TeacherSoftDeleteResultDTO>;
export type TeacherRestoreAttendanceResponse =
  ApiResponse<TeacherRestoreResultDTO>;
