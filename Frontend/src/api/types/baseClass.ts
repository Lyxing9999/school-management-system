export interface BaseClassDataDTO {
  id: string;
  name: string;
  grade: number;
  max_students: number;
  status: boolean;
  academic_year?: string;
  code?: string;
  class_room?: string | null;
  homeroom_teacher?: string | null;
  subjects?: string[] | null;
  students?: string[] | null;
  deleted: boolean;
  deleted_at?: string;
  deleted_by?: string;
  created_at: string;
  created_by: string;
  updated_at: string;
  updated_by: string;
}
