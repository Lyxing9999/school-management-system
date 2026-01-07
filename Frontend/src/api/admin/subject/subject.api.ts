import type { AxiosInstance } from "axios";
import type {
  AdminCreateSubject,
  AdminGetSubjectResponse,
  AdminUpdateSubject,
  SubjectStatus,
  AdminSubjectPaginatedListResponse,
  AdminSubjectNameSelectListResponse,
} from "./subject.dto";

export class SubjectApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/subjects"
  ) {}

  // ============
  // QUERY
  // ============
  async getSubjects(params?: {
    status?: SubjectStatus;
    page?: number;
    page_size?: number;
    search?: string | null;
  }): Promise<AdminSubjectPaginatedListResponse> {
    const res = await this.$api.get<AdminSubjectPaginatedListResponse>(
      this.baseURL,
      {
        params,
      }
    );
    return res.data;
  }

  async getSubject(id: string): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.get<AdminGetSubjectResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  async listSubjectNameSelect() {
    const res = await this.$api.get<AdminSubjectNameSelectListResponse>(
      `${this.baseURL}/names-select`
    );
    return res.data;
  }

  // ============
  // COMMANDS
  // ============
  async createSubject(
    data: AdminCreateSubject
  ): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.post<AdminGetSubjectResponse>(
      this.baseURL,
      data
    );
    return res.data;
  }

  async updateSubject(
    subjectId: string,
    data: Partial<AdminUpdateSubject>
  ): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.patch<AdminGetSubjectResponse>(
      `${this.baseURL}/${subjectId}`,
      data
    );
    return res.data;
  }
  async softDeleteSubject(subjectId: string): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.patch<AdminGetSubjectResponse>(
      `${this.baseURL}/${subjectId}/soft-delete`
    );
    return res.data;
  }

  async activateSubject(subjectId: string): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.patch<AdminGetSubjectResponse>(
      `${this.baseURL}/${subjectId}/activate`
    );
    return res.data;
  }

  async deactivateSubject(subjectId: string): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.patch<AdminGetSubjectResponse>(
      `${this.baseURL}/${subjectId}/deactivate`
    );
    return res.data;
  }
}
