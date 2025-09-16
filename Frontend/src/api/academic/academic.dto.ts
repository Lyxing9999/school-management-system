import { Role } from "~/api/types/enums/role.enum";
import type { ApiResponse } from "~/api/types/common/api-response.type";

/**
 * -------------------------------
 * Generic Admin API Response Wrapper
 * -------------------------------
 * Uses generics to avoid repeating ApiResponse for every entity
 */
export type AcademicApiResponse<T> = ApiResponse<T>;

export type AcademicFindClassDTO = {
  id: string;
  name: string;
  owner_id: string;
  grade: number;
  owner?: string;
  owner_name?: string;
  max_students: number;
  status: boolean;
  created_at?: string;
  updated_at?: string;
  deleted?: boolean;
  deleted_at?: string;
  deleted_by?: string;
};

export type AcademicFindClassDTOList = AcademicFindClassDTO[];

/**
 * -------------------------------
 * Academic API Response Wrapper
 * -------------------------------
 */
export type AcademicFindClassResponseDTO =
  AcademicApiResponse<AcademicFindClassDTO>;
export type AcademicFindClassResponseDTOList =
  AcademicApiResponse<AcademicFindClassDTOList>;
