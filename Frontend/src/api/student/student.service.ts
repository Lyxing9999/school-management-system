// ~/api/student/service.ts
import { useApiUtils } from "~/utils/useApiUtils";
import type {
  StudentClassListDTO,
  StudentAttendanceListDTO,
  StudentGradeListDTO,
  StudentScheduleListDTO,
  StudentAttendanceFilterDTO,
  StudentGradesFilterDTO,
  StudentScheduleFilterDTO,
} from "./student.dto";
import { StudentApi } from "./student.api";

export class StudentService {
  private safeApiCall = useApiUtils().safeApiCall;

  constructor(private studentApi: StudentApi) {}

  // ============
  // QUERY
  // ============

  async getMyClasses() {
    const { data } = await this.safeApiCall<StudentClassListDTO>(() =>
      this.studentApi.getMyClasses()
    );
    return data!;
  }

  async getMyAttendance(params?: StudentAttendanceFilterDTO) {
    const { data } = await this.safeApiCall<StudentAttendanceListDTO>(() =>
      this.studentApi.getMyAttendance(params)
    );
    return data!;
  }

  async getMyGrades(params?: StudentGradesFilterDTO) {
    const { data } = await this.safeApiCall<StudentGradeListDTO>(() =>
      this.studentApi.getMyGrades(params)
    );
    return data!;
  }

  async getMySchedule(params?: StudentScheduleFilterDTO) {
    const { data } = await this.safeApiCall<StudentScheduleListDTO>(() =>
      this.studentApi.getMySchedule(params)
    );
    return data!;
  }
}
