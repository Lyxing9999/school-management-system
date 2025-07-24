import type { Teacher, TeacherInfo } from "~/types/models/Teacher";

export class TeacherModel implements Teacher {
  _id?: string;
  user_id: string;
  phone_number?: string;
  teacher_info: TeacherInfo;

  constructor(data: Partial<Teacher> = {}) {
    this._id = data._id;
    this.user_id = data.user_id ?? "";
    this.phone_number = data.phone_number?.trim();
    this.teacher_info = {
      teacher_id: data.teacher_info?.teacher_id ?? "",
      lecturer_name: data.teacher_info?.lecturer_name?.trim(),
      subjects: data.teacher_info?.subjects ?? [],
      created_at: data.teacher_info?.created_at ?? new Date().toISOString(),
      updated_at: data.teacher_info?.updated_at,
    };
  }

  toDict(): Record<string, any> {
    const result: Record<string, any> = {
      user_id: this.user_id,
      teacher_info: {
        teacher_id: this.teacher_info.teacher_id,
        lecturer_name: this.teacher_info.lecturer_name,
        subjects: this.teacher_info.subjects,
        created_at: this.teacher_info.created_at,
        updated_at: this.teacher_info.updated_at,
      },
    };

    if (this._id) result._id = this._id;
    if (this.phone_number) result.phone_number = this.phone_number;

    return result;
  }
}
