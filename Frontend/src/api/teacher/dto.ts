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
 * Python: TeacherGradeListDTO
 */
export interface TeacherGradeListDTO {
  items: GradeDTO[];
}

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

export interface TeacherScheduleListDTO {
  items: ScheduleDTO[];
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
export type TeacherListClassGradesResponse = ApiResponse<TeacherGradeListDTO>;

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
