import type { AxiosInstance } from "axios";
import type {
  AdminCreateSubject,
  AdminUpdateSubject,
  AdminSubjectResponse,
} from "./dto";

export class SubjectApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/subject"
  ) {}

  async getSubjects(): Promise<AdminSubjectResponse> {
    const res = await this.$api.get<AdminSubjectResponse>(this.baseURL);
    return res.data;
  }

  async getSubjectById(id: string): Promise<AdminSubjectResponse> {
    const res = await this.$api.get<AdminSubjectResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  async createSubject(data: AdminCreateSubject): Promise<AdminSubjectResponse> {
    const res = await this.$api.post<AdminSubjectResponse>(this.baseURL, data);
    return res.data;
  }

  async updateSubject(
    id: string,
    data: AdminUpdateSubject
  ): Promise<AdminSubjectResponse> {
    const res = await this.$api.patch<AdminSubjectResponse>(
      `${this.baseURL}/${id}`,
      data
    );
    return res.data;
  }

  async deleteSubject(id: string): Promise<AdminSubjectResponse> {
    const res = await this.$api.delete<AdminSubjectResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }
}
