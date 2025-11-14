import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { ClassBaseDataDTO } from "~/api/types/class.dto";

export interface AdminGetClassData extends ClassBaseDataDTO {}

export interface AdminCreateClass {
  name: string;
  grade: number;
  max_students: number;
  academic_year?: string;
  code?: string;
  status?: boolean;
}

export interface AdminUpdateClass {
  name?: string;
  owner_id?: string;
  max_students?: number;
  grade?: number;
  status?: boolean;
  code?: string;
  class_room?: string | null;
  academic_year?: string;
  homeroom_teacher?: string | null;
  subjects?: string[] | null;
  students?: string[] | null;
}

export interface AdminAssignTeacher {
  teacher_id: string;
}
export interface AdminUnassignTeacher {
  teacher_id: string;
}
export interface AdminAssignStudent {
  student_id: string;
}
export interface AdminUnassignStudent {
  student_id: string;
}

export interface AdminFindTeacherSelect {
  id: string;
  staff_name: string;
}
export type AdminGetTeacherSelectResponse = ApiResponse<
  AdminFindTeacherSelect[]
>;

export type AdminGetClassResponse = ApiResponse<AdminGetClassData>;
export type AdminGetAllClassesResponse = ApiResponse<AdminGetClassData[]>;
