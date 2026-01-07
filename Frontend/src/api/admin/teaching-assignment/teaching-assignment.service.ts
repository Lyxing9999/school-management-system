import { TeachingAssignmentApi } from "./teaching-assignment.api";
import type {
  AdminTeachingAssignmentDTO,
  AdminTeachingAssignmentListDTO,
  AdminTeachingAssignmentWriteResultDTO,
  AdminAssignSubjectTeacherPayload,
} from "./teaching-assignment.dto";
import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";

export class TeachingAssignmentService {
  private callApi = useApiUtils().callApi;

  constructor(private api: TeachingAssignmentApi) {}

  async listForClass(
    classId: string,
    params?: { show_deleted?: "all" | "active" | "deleted" },
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminTeachingAssignmentListDTO>(
      () => this.api.listForClass(classId, params),
      options
    );
    return data as AdminTeachingAssignmentListDTO;
  }

  async assignForClass(
    classId: string,
    payload: AdminAssignSubjectTeacherPayload,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminTeachingAssignmentWriteResultDTO>(
      () => this.api.assignForClass(classId, payload),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data as AdminTeachingAssignmentWriteResultDTO;
  }

  async unassignForClass(
    classId: string,
    subjectId: string,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<{
      deleted: boolean;
      modified_count: number;
    }>(() => this.api.unassignForClass(classId, { subject_id: subjectId }), {
      showSuccess: true,
      ...(options ?? {}),
    });
    return data as { deleted: boolean; modified_count: number };
  }
}
