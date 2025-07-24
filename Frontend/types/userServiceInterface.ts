import type { AuthUser as AuthUserType } from "~/types/auth";
import type { Student as StudentType } from "~/types/models/Student";
import type { Teacher as TeacherType } from "~/types/models/Teacher";

export type Role = "student" | "teacher" | "admin";

export type AuthUser = {
  id: string;
  permission_level: string;
  created_at: string;
  updated_at?: string;
};

export type UserDetail =
  | { student_info: StudentType }
  | { teacher_info: TeacherType }
  | { admin_info: AuthUserType };

export type UserFormInput = {
  username: string;
  email?: string;
  password: string;
  role: string;
};

export enum CreateUserFormFields {
  Username = "username",
  Email = "email",
  Password = "password",
  Role = "role",
}

export interface RoleDataMap {
  student: StudentType;
  teacher: TeacherType;
  admin: AuthUserType;
}

export interface UserDetailResponse<T = any> {
  role: Role;
  data: T;
}
