import type { AxiosInstance } from "axios";
import type {
  AdminTeachingAssignmentListResponse,
  AdminTeachingAssignmentWriteResponse,
  AdminTeachingAssignmentDeleteResponse,
  AdminAssignSubjectTeacherPayload,
  AdminUnassignSubjectTeacherPayload,
} from "./teaching-assignment.dto";

export class TeachingAssignmentApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/classes"
  ) {}

  async listForClass(
    classId: string,
    params?: { show_deleted?: "all" | "active" | "deleted" }
  ) {
    return this.$api
      .get<AdminTeachingAssignmentListResponse>(
        `${this.baseURL}/${classId}/assignments`,
        {
          params: { show_deleted: params?.show_deleted ?? "active" },
        }
      )
      .then((r) => r.data);
  }

  async assignForClass(
    classId: string,
    payload: AdminAssignSubjectTeacherPayload
  ) {
    return this.$api
      .post<AdminTeachingAssignmentWriteResponse>(
        `${this.baseURL}/${classId}/assignments`,
        payload
      )
      .then((r) => r.data);
  }

  async unassignForClass(
    classId: string,
    payload: AdminUnassignSubjectTeacherPayload
  ) {
    return this.$api
      .delete<AdminTeachingAssignmentDeleteResponse>(
        `${this.baseURL}/${classId}/assignments`,
        {
          data: payload,
        }
      )
      .then((r) => r.data);
  }
}
