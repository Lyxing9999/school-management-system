import type { AxiosInstance } from "axios";
import type {
  AdminCreateClass,
  AdminGetClassListResponse,
  AdminGetClassResponse,
  AdminClassNameSelectListResponse,
  AdminStudentsInClassSelectResponse,
  AdminUpdateClassRelationsResponse,
  AdminUpdateClassRelationsDTO,
  SearchStudentsParams,
  AdminStudentSelectPagedResultResponse,
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
    return this.$api
      .get<AdminGetClassListResponse>(this.baseURL)
      .then((res) => res.data);
  }

  async getClass(classId: string) {
    return this.$api
      .get<AdminGetClassResponse>(`${this.baseURL}/${classId}`)
      .then((res) => res.data);
  }

  async listClassNameSelect() {
    return this.$api
      .get<AdminClassNameSelectListResponse>(`${this.baseURL}/names-select`)
      .then((res) => res.data);
  }

  async listStudentsInClass(classID: string) {
    return this.$api
      .get<AdminStudentsInClassSelectResponse>(
        `${this.baseURL}/${classID}/students`
      )
      .then((res) => res.data);
  }
  async searchStudentsForEnrollmentSelect(
    classID: string,
    params: SearchStudentsParams,
    signal?: AbortSignal
  ): Promise<AdminStudentSelectPagedResultResponse> {
    return this.$api
      .get<AdminStudentSelectPagedResultResponse>(
        `${this.baseURL}/${classID}/enrollment-student-select/search`,
        {
          params: {
            q: params.q,
            limit: params.limit ?? 30,
            cursor: params.cursor ?? undefined,
          },
          signal,
        }
      )
      .then((res) => res.data);
  }
  // ============
  // COMMANDS
  // ============
  async createClass(data: AdminCreateClass): Promise<AdminGetClassResponse> {
    return this.$api
      .post<AdminGetClassResponse>(`${this.baseURL}`, data)
      .then((res) => res.data);
  }

  async assignClassTeacher(classID: string, teacherId: string) {
    return this.$api
      .patch<AdminGetClassResponse>(`${this.baseURL}/${classID}/teacher`, {
        teacher_id: teacherId,
      })
      .then((res) => res.data);
  }

  async unassignClassTeacher(classID: string) {
    return this.$api
      .delete<AdminGetClassResponse>(`${this.baseURL}/${classID}/teacher`)
      .then((res) => res.data);
  }
  async enrollStudent(classID: string, studentID: string) {
    return this.$api
      .post<AdminGetClassResponse>(`${this.baseURL}/${classID}/students`, {
        student_id: studentID,
      })
      .then((res) => res.data);
  }

  async unenrollStudent(classID: string, studentID: string) {
    return this.$api
      .delete<AdminGetClassResponse>(
        `${this.baseURL}/${classID}/students/${studentID}`
      )
      .then((res) => res.data);
  }
  async softDeleteClass(classId: string) {
    return this.$api
      .delete<AdminGetClassResponse>(`${this.baseURL}/${classId}/soft-delete`)
      .then((res) => res.data);
  }

  async updateRelations(
    classID: string,
    payload: AdminUpdateClassRelationsDTO
  ) {
    return this.$api
      .put<AdminUpdateClassRelationsResponse>(
        `${this.baseURL}/${classID}/relations`,
        payload
      )
      .then((res) => res.data);
  }
}
