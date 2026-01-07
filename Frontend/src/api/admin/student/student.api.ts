import type { AxiosInstance } from "axios";
import type {
  AdminCreateStudent,
  AdminCreateStudentResponse,
  AdminUpdateStudent,
  AdminStudentListSelectResponse,
  StudentBaseDataResponse,
} from "~/api/admin/student/student.dto";

export class StudentApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/students"
  ) {}

  async getStudentUserId(id: string): Promise<StudentBaseDataResponse> {
    const res = await this.$api.get<StudentBaseDataResponse>(
      `${this.baseURL}/user/${id}`
    );
    return res.data;
  }

  async updateStudentUserId(
    id: string,
    payload: AdminUpdateStudent
  ): Promise<StudentBaseDataResponse> {
    const res = await this.$api.patch<StudentBaseDataResponse>(
      `${this.baseURL}/user/${id}`,
      payload
    );
    return res.data;
  }

  /**
   * Create a new student (IAM + Profile)
   */
  async createStudent(
    payload: AdminCreateStudent
  ): Promise<AdminCreateStudentResponse> {
    const res = await this.$api.post<AdminCreateStudentResponse>(
      this.baseURL,
      payload
    );
    return res.data;
  }
  async listStudentNamesSelect(): Promise<AdminStudentListSelectResponse> {
    const res = await this.$api.get<AdminStudentListSelectResponse>(
      `${this.baseURL}/student-select`
    );
    return res.data;
  }
  /**
   * Get single student info
   */
  // async getStudentInfo(id: string): Promise<AdminGetStudentResponse> {
  //   const res = await this.$api.get<AdminGetStudentResponse>(
  //     `${this.baseURL}/${id}`
  //   );
  //   return res.data;
  // }

  // async updateStudentInfo(
  //   id: string,
  //   payload: AdminUpdateStudent
  // ): Promise<AdminGetStudentResponse> {
  //   const res = await this.$api.patch<AdminGetStudentResponse>(
  //     `${this.baseURL}/${id}`,
  //     payload
  //   );
  //   return res.data;
  // }

  // async getStudents(
  //   page = 1,
  //   pageSize = 10
  // ): Promise<AdminGetPageStudentResponse> {
  //   const res = await this.$api.get<AdminGetPageStudentResponse>(this.baseURL, {
  //     params: { page, page_size: pageSize },
  //   });
  //   return res.data;
  // }

  // async getStudentSelect(): Promise<AdminStudentListSelectResponse> {
  //   const res = await this.$api.get<AdminStudentListSelectResponse>(
  //     `${this.baseURL}/select`
  //   );
  //   return res.data;
  // }
}
