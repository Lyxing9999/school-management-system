import type { Student, StudentInfo } from "~/types/models/Student";

import { Role } from "~/types/models/User";

export class StudentModel implements Student {
  _id?: string;
  user_id: string;
  role: Role;
  username: string;
  email?: string;
  password?: string;
  student_info: StudentInfo;

  constructor(data: Partial<Student> = {}) {
    this._id = data._id;
    this.user_id = data.user_id ?? "";
    this.role = data.role ?? Role.student;
    this.username = data.username?.trim() ?? "";
    this.email = data.email?.trim();
    this.password = data.password?.trim();

    this.student_info = {
      student_id: data.student_info?.student_id ?? "",
      grade: data.student_info?.grade,
      class_ids: data.student_info?.class_ids ?? [],
      major: data.student_info?.major,
      birth_date: data.student_info?.birth_date,
      batch: data.student_info?.batch,
      address: data.student_info?.address,
      phone_number: data.student_info?.phone_number,
      email: data.student_info?.email,
      attendance_record: data.student_info?.attendance_record ?? {},
      courses_enrolled: data.student_info?.courses_enrolled ?? [],
      scholarships: data.student_info?.scholarships ?? [],
      current_gpa: data.student_info?.current_gpa ?? 0.0,
      remaining_credits: data.student_info?.remaining_credits ?? 0,
      created_at: data.student_info?.created_at ?? new Date().toISOString(),
      updated_at: data.student_info?.updated_at,
    };
  }

  toDict(includePassword = false): Record<string, any> {
    const result: Record<string, any> = {
      user_id: this.user_id,
      role: this.role,
      username: this.username,
      student_info: { ...this.student_info },
    };

    if (this._id) result._id = this._id;
    if (this.email) result.email = this.email;
    if (includePassword && this.password) result.password = this.password;

    return result;
  }
}
