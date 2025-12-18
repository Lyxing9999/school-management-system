import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import { StudentApi } from "./student.api";

import type {
  AdminCreateStudent,
  AdminGetStudentData,
  AdminUpdateStudent,
  StudentBaseDataDTO,
  AdminStudentNameSelectDTO,
} from "./student.dto";

export class StudentService {
  private callApi = useApiUtils().callApi;

  constructor(private studentApi: StudentApi) {}

  // ==========================================================
  // 🟢 CREATE
  // ==========================================================
  async createStudent(payload: AdminCreateStudent, options?: ApiCallOptions) {
    const data = await this.callApi<AdminGetStudentData>(
      () => this.studentApi.createStudent(payload),
      options
    );
    // Return data! (Non-null assertion because callApi handles errors)
    return data!;
  }

  async getStudentUserId(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<StudentBaseDataDTO>(
      () => this.studentApi.getStudentUserId(id),
      options
    );
    return data!;
  }

  async updateStudentUserId(
    id: string,
    payload: AdminUpdateStudent,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<StudentBaseDataDTO>(
      () => this.studentApi.updateStudentUserId(id, payload),
      options
    );
    return data!;
  }
  async listStudentNamesSelect(options?: ApiCallOptions) {
    const data = await this.callApi<AdminStudentNameSelectDTO>(
      () => this.studentApi.listStudentNamesSelect(),
      options
    );
    return data!;
  }
  // ==========================================================
  // READ (Get Single)
  // ==========================================================
  // async getStudentInfo(id: string, options?: ApiCallOptions) {
  //   const data = await this.callApi<AdminGetStudentResponse>(
  //     () => this.studentApi.getStudentInfo(id),
  //     options
  //   );
  //   return data!;
  // }

  // ==========================================================
  // UPDATE
  // ==========================================================
  // async updateStudent(
  //   id: string,
  //   payload: AdminUpdateStudent,
  //   options?: ApiCallOptions
  // ) {
  //   const data = await this.callApi<AdminGetStudentResponse>(
  //     () => this.studentApi.updateStudentInfo(id, payload),
  //     options
  //   );
  //   return data!;
  // }

  // ==========================================================
  //  (Pagination) - Optional
  // ==========================================================
  // async getStudents(page = 1, pageSize = 10, options?: ApiCallOptions) {
  //   const data = await this.callApi<AdminGetPageStudentResponse>(
  //     () => this.studentApi.getStudents(page, pageSize),
  //     options
  //   );
  //   return data!;
  // }
}
