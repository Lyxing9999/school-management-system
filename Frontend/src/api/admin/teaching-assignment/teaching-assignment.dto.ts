import type { ApiResponse } from "~/api/types/common/api-response.type";

export type AdminTeachingAssignmentDTO = {
  id: string;
  class_id: string;
  subject_id: string;
  teacher_id: string;

  class_name?: string | null;
  subject_label?: string | null;
  teacher_name?: string | null;

  lifecycle?: {
    created_at?: string | null;
    updated_at?: string | null;
    deleted_at?: string | null;
    deleted_by?: string | null;
  };
};

export type AdminTeachingAssignmentListDTO = {
  items: AdminTeachingAssignmentDTO[];
};

export type AdminAssignSubjectTeacherPayload = {
  subject_id: string;
  teacher_id: string;
  overwrite?: boolean;
};

export type AdminUnassignSubjectTeacherPayload = {
  subject_id: string;
};

export type AdminTeachingAssignmentWriteResultDTO = {
  id: string;
  class_id: string;
  subject_id: string;
  teacher_id: string;
  mode: "created" | "updated";
};

export type AdminTeachingAssignmentListResponse =
  ApiResponse<AdminTeachingAssignmentListDTO>;
export type AdminTeachingAssignmentWriteResponse =
  ApiResponse<AdminTeachingAssignmentWriteResultDTO>;
export type AdminTeachingAssignmentDeleteResponse = ApiResponse<{
  deleted: boolean;
  modified_count: number;
}>;
