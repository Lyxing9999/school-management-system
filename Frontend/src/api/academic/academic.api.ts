import type { AxiosInstance } from "axios";
import type {
  AcademicGetStudentResponse,
  AcademicCreateClassData,
  AcademicGetClassesResponse,
  AcademicGetTeacherSelectResponseList,
  AcademicStudentInfoUpdate,
  AcademicGetStudentPageResponse,
  AcademicCreateStudentData,
  AcademicUpdateStudentData,
  AcademicStudentInfoResponse,
} from "~/api/academic/academic.dto";

export class AcademicApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/academic") {}
  //
  // ------------------------- student api   -----------------------------//
  //
  async getStudentsPage(
    page: number,
    pageSize: number
  ): Promise<AcademicGetStudentPageResponse> {
    const response = await this.$api.get<AcademicGetStudentPageResponse>(
      `${this.baseURL}/students`,
      {
        params: {
          page,
          pageSize,
        },
      }
    );
    console.log(page, pageSize);
    return response.data;
  }

  async updateStudent(user_id: string, payload: AcademicUpdateStudentData) {
    const response = await this.$api.patch<AcademicGetStudentResponse>(
      `${this.baseURL}/student/${user_id}`,
      payload
    );
    return response.data;
  }

  async deleteStudent(user_id: string) {
    const response = await this.$api.delete<AcademicGetStudentResponse>(
      `${this.baseURL}/student/${user_id}`
    );
    return response.data;
  }

  async createStudent(payload: AcademicCreateStudentData) {
    const response = await this.$api.post<AcademicGetStudentResponse>(
      `${this.baseURL}/student`,
      payload
    );
    return response.data;
  }

  async getStudentInfo(user_id: string) {
    const response = await this.$api.get<AcademicStudentInfoResponse>(
      `${this.baseURL}/student-info/${user_id}`
    );
    return response.data;
  }

  async updateStudentInfo(user_id: string, payload: AcademicStudentInfoUpdate) {
    const formData = new FormData();

    Object.entries(payload).forEach(([key, value]) => {
      if (value === undefined || value === null || key === "photo_file") return;
      formData.append(
        key,
        Array.isArray(value) ? JSON.stringify(value) : (value as string | Blob)
      );
    });

    if (payload.photo_file) {
      formData.append("photo_url", payload.photo_file); // matches backend
    }

    // Debug
    for (const [key, value] of formData.entries()) {
      console.log(key, value);
    }

    const response = await this.$api.patch<AcademicStudentInfoResponse>(
      `${this.baseURL}/student-info/${user_id}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    return response.data;
  }

  async getClasses(): Promise<AcademicGetClassesResponse> {
    const response = await this.$api.get<AcademicGetClassesResponse>(
      `${this.baseURL}/classes`
    );
    return response.data;
  }
  async createClass(
    payload: AcademicCreateClassData
  ): Promise<AcademicGetClassesResponse> {
    const response = await this.$api.post<AcademicGetClassesResponse>(
      `${this.baseURL}/classes`,
      payload
    );
    return response.data;
  }

  async getTeacherForSelect(
    searchText: string
  ): Promise<AcademicGetTeacherSelectResponseList> {
    const response = await this.$api.get<AcademicGetTeacherSelectResponseList>(
      `${this.baseURL}/staff_name_select`,
      {
        params: {
          search_text: searchText,
        },
      }
    );
    return response.data;
  }

  async getTeacherNames(): Promise<AcademicGetTeacherSelectResponseList> {
    const response = await this.$api.get<AcademicGetTeacherSelectResponseList>(
      `${this.baseURL}/teacher_names`
    );
    return response.data;
  }
}
