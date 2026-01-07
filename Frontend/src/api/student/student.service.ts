// ~/api/student/student.service.ts
import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";
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
  private callApi = useApiUtils().callApi;

  constructor(private studentApi: StudentApi) {}

  // ============
  // QUERY METHODS
  // ============

  /**
   * GET /student/me/classes
   */
  async getMyClasses(options?: ApiCallOptions) {
    const data = await this.callApi<StudentClassListDTO>(
      () => this.studentApi.getMyClasses(),
      {
        // sensible default: show error toast if it fails
        showError: true,
        ...(options ?? {}),
      }
    );
    return data!;
  }

  /**
   * GET /student/me/attendance
   * Optional filters: class_id, date_from, date_to, etc. (depending on your DTO)
   */
  async getMyAttendance(
    params?: StudentAttendanceFilterDTO,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<StudentAttendanceListDTO>(
      () => this.studentApi.getMyAttendance(params),
      {
        showError: true,
        ...(options ?? {}),
      }
    );
    return data!;
  }

  /**
   * GET /student/me/grades
   */
  async getMyGrades(options?: ApiCallOptions) {
    const data = await this.callApi<StudentGradeListDTO>(
      () => this.studentApi.getMyGrades(),
      {
        showError: true,
        ...(options ?? {}),
      }
    );
    return data!;
  }

  /**
   * GET /student/me/schedule
   */
  async getMySchedule(
    params?: StudentScheduleFilterDTO,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<StudentScheduleListDTO>(
      () => this.studentApi.getMySchedule(params),
      {
        showError: true,
        ...(options ?? {}),
      }
    );
    return data!;
  }
}
