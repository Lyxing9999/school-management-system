import type { AxiosInstance } from "axios";
import type {
  AdminStudentInfoResponse,
  AdminUpdateStudentInfo,
} from "./student.dto";

export class StudentApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/student"
  ) {}

  async getStudentInfo(id: string): Promise<AdminStudentInfoResponse> {
    const res = await this.$api.get<AdminStudentInfoResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  async updateStudentInfo(
    id: string,
    studentData: AdminUpdateStudentInfo & { photo_file?: File | null }
  ) {
    const formData = new FormData();
    Object.entries(studentData).forEach(([key, value]) => {
      if (value === undefined || value === null || key === "photo_file") return;
      formData.append(
        key,
        Array.isArray(value) ? JSON.stringify(value) : (value as string | Blob)
      );
    });
    if (studentData.photo_file)
      formData.append("photo_url", studentData.photo_file);
    const res = await this.$api.patch<AdminStudentInfoResponse>(
      `${this.baseURL}/${id}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return res.data;
  }
}
