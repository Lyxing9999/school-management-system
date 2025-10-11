import type { AxiosInstance } from "axios";
import type {
  AcademicGetStudentResponse,
  AcademicCreateClassPayload,
  AcademicGetClassResponse,
  AcademicGetClassesResponse,
  AcademicGetTeacherSelectResponseList,
} from "~/api/academic/academic.dto";

export class AcademicApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/academic") {}
  async getStudents(
    page: number,
    pageSize: number
  ): Promise<AcademicGetStudentResponse> {
    const response = await this.$api.get<AcademicGetStudentResponse>(
      `${this.baseURL}/students`,
      {
        params: {
          page,
          pageSize,
        },
      }
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
    payload: AcademicCreateClassPayload
  ): Promise<AcademicGetClassResponse> {
    const response = await this.$api.post<AcademicGetClassResponse>(
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
