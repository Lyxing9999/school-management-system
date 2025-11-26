import type { AxiosInstance } from "axios";
import type {
  AdminCreateSubjectDTO,
  AdminGetSubjectListResponse,
  AdminGetSubjectResponse
} from "./dto";

export class SubjectApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/subjects"
  ) {}

  // ============
  // QUERY
  // ============
  async getSubjects(): Promise<AdminGetSubjectListResponse> {
    const res = await this.$api.get<AdminGetSubjectListResponse>(this.baseURL);
    return res.data;
  }

  async getSubject(id: string): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.get<AdminGetSubjectResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  // ============
  // COMMANDS
  // ============
  async createSubject(
    data: AdminCreateSubjectDTO
  ): Promise<AdminGetSubjectResponse> {
    const res = await this.$api.post<AdminGetSubjectResponse>(
      this.baseURL,
      data
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
