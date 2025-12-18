import type { AxiosInstance } from "axios";
import type {
  AdminCreateClass,
  AdminGetClassListResponse,
  AdminGetClassResponse,
  AdminClassNameSelectListResponse,
  AdminStudentsInClassSelectResponse,
} from "./class.dto";

export class ClassApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/classes"
  ) {}

  // ============
  // QUERY
  // ============

  async getClasses() {
    const res = await this.$api.get<AdminGetClassListResponse>(this.baseURL);
    return res.data;
  }

  async getClass(classId: string) {
    const res = await this.$api.get<AdminGetClassResponse>(
      `${this.baseURL}/${classId}`
    );
    return res.data;
  }

  async listClassNameSelect() {
    const res = await this.$api.get<AdminClassNameSelectListResponse>(
      `${this.baseURL}/names-select`
    );
    return res.data;
  }

  async listStudentsInClass(classID: string) {
    const res = await this.$api.get<AdminStudentsInClassSelectResponse>(
      `${this.baseURL}/${classID}/students`
    );
    return res.data;
  }
  // ============
  // COMMANDS
  // ============
  async createClass(data: AdminCreateClass): Promise<AdminGetClassResponse> {
    const res = await this.$api.post<AdminGetClassResponse>(
      `${this.baseURL}`,
      data
    );
    return res.data;
  }

  async assignClassTeacher(classID: string, teacherId: string) {
    const res = await this.$api.patch<AdminGetClassResponse>(
      `${this.baseURL}/${classID}/teacher`,
      { teacher_id: teacherId }
    );
    return res.data;
  }

  async unassignClassTeacher(classID: string) {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${classID}/teacher`
    );
    return res.data;
  }
  async enrollStudent(classID: string, studentID: string) {
    const res = await this.$api.post<AdminGetClassResponse>(
      `${this.baseURL}/${classID}/students`,
      { student_id: studentID }
    );
    return res.data;
  }

  async unenrollStudent(classID: string, studentID: string) {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${classID}/students/${studentID}`
    );
    return res.data;
  }
  async softDeleteClass(classId: string) {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${classId}/soft-delete`
    );
    return res.data;
  }
}
