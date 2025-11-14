import type { AxiosInstance } from "axios";
import type {
  AdminCreateClass,
  AdminGetClassResponse,
  AdminUpdateClass,
  AdminAssignTeacher,
  AdminAssignStudent,
  AdminUnassignStudent,
  AdminGetAllClassesResponse,
} from "./dto";

export class ClassApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/admin") {}

  async createClass(data: AdminCreateClass): Promise<AdminGetClassResponse> {
    const res = await this.$api.post<AdminGetClassResponse>(this.baseURL, data);
    return res.data;
  }

  async updateClass(
    id: string,
    data: AdminUpdateClass
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.patch<AdminGetClassResponse>(
      `${this.baseURL}/classes/${id}`,
      data
    );
    return res.data;
  }

  async softDeleteClass(id: string): Promise<AdminGetClassResponse> {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${id}/soft-delete`
    );
    return res.data;
  }

  async getAllClasses(): Promise<AdminGetAllClassesResponse> {
    const res = await this.$api.get<AdminGetAllClassesResponse>(
      `${this.baseURL}/classes`
    );
    return res.data;
  }

  async getClassById(id: string): Promise<AdminGetClassResponse> {
    const res = await this.$api.get<AdminGetClassResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  async assignTeacher(
    id: string,
    data: AdminAssignTeacher
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.patch<AdminGetClassResponse>(
      `${this.baseURL}/${id}/teacher`,
      data
    );
    return res.data;
  }

  async unassignTeacher(id: string): Promise<AdminGetClassResponse> {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${id}/teacher`
    );
    return res.data;
  }

  async assignStudent(
    id: string,
    data: AdminAssignStudent
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.patch<AdminGetClassResponse>(
      `${this.baseURL}/${id}/students`,
      data
    );
    return res.data;
  }

  async removeStudent(
    id: string,
    data: AdminUnassignStudent
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${id}/students`,
      { data }
    );
    return res.data;
  }
}
