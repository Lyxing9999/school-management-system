// ~/api/student/service.ts
import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import type { AdminUpdateStudentInfo } from "./dto";
import type { StudentInfoBaseDataDTO } from "~/api/types/student.dto";
import { StudentApi } from "../student/api";

export class StudentService {
  private callApi = useApiUtils().callApi;

  constructor(private studentApi: StudentApi) {}

  // Query
  async getStudentInfo(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<StudentInfoBaseDataDTO>(
      () => this.studentApi.getStudentInfo(id),
      options
    );
    return data!;
  }

  // Command
  async updateStudentInfo(
    id: string,
    studentData: AdminUpdateStudentInfo,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<StudentInfoBaseDataDTO>(
      () => this.studentApi.updateStudentInfo(id, studentData),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }
}
