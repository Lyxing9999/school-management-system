import { Role } from "~/api/types/enums/role.enum";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { UserBaseDataDTO } from "~/api/types/userBase";

export type AcademicApiResponse<T> = ApiResponse<T>;

export interface AcademicGetStudentData extends UserBaseDataDTO {}

export interface AcademicGetStudentsPayload {
  students: AcademicGetStudentData[];
  total: number;
}

export interface AcademicBaseClassDataDTO {
  id: string;
  name: string;
  grade: number;
  max_students: number;
  status: boolean;
  homeroom_teacher: string | null;
  subjects: string[] | null;
  students: string[] | null;
  deleted: boolean;
  deleted_at?: string;
  deleted_by?: string;
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
}

export interface AcademicCreateClassPayload {
  name: string;
  grade: number;
  max_students: number;
  status: boolean;
  homeroom_teacher: string | null;
  subjects: string[] | null;
  students: string[] | null;
}

export type AcademicGetClassResponse =
  AcademicApiResponse<AcademicBaseClassDataDTO>;

export type AcademicGetClassesResponse = AcademicApiResponse<
  AcademicBaseClassDataDTO[]
>;

export interface AcademicGetTeacherSelect {
  user_id: string;
  staff_name: string;
}
export type AcademicGetTeacherSelectResponseList = AcademicApiResponse<
  AcademicGetTeacherSelect[]
>;

export type AcademicGetStudentResponse =
  AcademicApiResponse<AcademicGetStudentsPayload>;

/**
 * -------------------------------
 * Generic Admin API Response Wrapper
 * -------------------------------
 * Uses generics to avoid repeating ApiResponse for every entity
 */

// export type AcademicFindClassDTO = {
//   id: string;
//   name: string;
//   owner_id: string;
//   grade: number;
//   owner?: string;
//   owner_name?: string;
//   max_students: number;
//   status: boolean;
//   created_at?: string;
//   updated_at?: string;
//   deleted?: boolean;
//   deleted_at?: string;
//   deleted_by?: string;
// };

// export type AcademicFindClassDTOList = AcademicFindClassDTO[];

/**
 * -------------------------------
 * Academic API Response Wrapper
 * -------------------------------
 */
// export type AcademicFindClassResponseDTO =
//   AcademicApiResponse<AcademicFindClassDTO>;
// export type AcademicFindClassResponseDTOList =
//   AcademicApiResponse<AcademicFindClassDTOList>;
