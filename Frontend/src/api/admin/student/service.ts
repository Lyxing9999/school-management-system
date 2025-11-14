import { useApiUtils } from "~/utils/useApiUtils";
import type { AdminUpdateStudentInfo } from "./dto";
import type { StudentInfoBaseDataDTO } from "~/api/types/student.dto";
import { StudentApi } from "../student/api";

export class StudentService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private studentApi: StudentApi) {}

  async getStudentInfo(id: string) {
    const { data } = await this.safeApiCall<StudentInfoBaseDataDTO>(() =>
      this.studentApi.getStudentInfo(id)
    );
    return data!;
  }

  async updateStudentInfo(id: string, studentData: AdminUpdateStudentInfo) {
    const { data } = await this.safeApiCall<StudentInfoBaseDataDTO>(() =>
      this.studentApi.updateStudentInfo(id, studentData)
    );
    return data!;
  }
}
