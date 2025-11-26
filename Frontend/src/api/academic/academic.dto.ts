import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { UserBaseDataDTO } from "~/api/types/user.dto";
import type { StudentInfoBaseDataDTO } from "~/api/types/student.dto";
import type { ClassBaseDataDTO } from "~/api/types/school.dto";
import { Role } from "~/api/types/enums/role.enum";

/* -------------------------------------------------------------------------- */
/*                                Common Types                                */
/* -------------------------------------------------------------------------- */
export type AcademicApiResponse<T> = ApiResponse<T>;

/* -------------------------------------------------------------------------- */
/*                                  Payloads                                  */
/* -------------------------------------------------------------------------- */
export interface AcademicStudentData extends UserBaseDataDTO {}

export interface AcademicStudentInfoData extends StudentInfoBaseDataDTO {}

export interface AcademicCreateStudentData {
  username?: string;
  email: string;
  password: string;
  role?: Role.STUDENT;
}

export interface AcademicUpdateStudentData {
  username?: string;
  email?: string;
  password?: string;
}

export interface AcademicCreateClassData {
  name: string;
  grade: number;
  max_students: number;
  status: boolean;
  homeroom_teacher: string | null;
  subjects: string[] | null;
  students: string[] | null;
}

/* -------------------------------------------------------------------------- */
/*                                  Responses                                 */
/* -------------------------------------------------------------------------- */
export interface AcademicGetTeacherSelect {
  user_id: string;
  staff_name: string;
}

export type AcademicGetTeacherSelectResponseList = AcademicApiResponse<
  AcademicGetTeacherSelect[]
>;

export type AcademicGetClassData = AcademicApiResponse<ClassBaseDataDTO[]>;

export type AcademicGetClassesResponse = AcademicApiResponse<
  AcademicGetClassData[]
>;

export interface AcademicGetStudentsPageData {
  users: AcademicStudentData[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type AcademicGetStudentResponse =
  AcademicApiResponse<AcademicStudentData>;

export type AcademicGetStudentPageResponse =
  AcademicApiResponse<AcademicGetStudentsPageData>;

export type AcademicStudentInfoCreate = StudentInfoBaseDataDTO;

export type AcademicStudentInfoUpdate = Partial<StudentInfoBaseDataDTO>;

export type AcademicStudentInfoResponse =
  AcademicApiResponse<StudentInfoBaseDataDTO>;
