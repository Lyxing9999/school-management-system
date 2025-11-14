export interface SubjectBaseDataDTO {
  id: string;
  name: string;
  teacher_id: string[];
  created_at: string;
  updated_at: string;
  created_by: string;
  deleted_at: string | null;
}
