import type { AxiosInstance } from "axios";
import type {
  AdminCreateStudent,
  AdminCreateStudentResponse,
  AdminGetStudentResponse,
  AdminUpdateStudent,
  AdminGetPageStudentResponse,
  AdminStudentListSelectResponse,
} from "~/api/admin/student/student.dto";

export class StudentApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/students"
  ) {}

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
