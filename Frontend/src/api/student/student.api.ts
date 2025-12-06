// ~/api/student/api.ts
import type { AxiosInstance } from "axios";
import type {
  StudentGetClassesResponse,
  StudentGetAttendanceResponse,
  StudentGetGradesResponse,
  StudentGetScheduleResponse,
  StudentAttendanceFilterDTO,
  StudentGradesFilterDTO,
  StudentScheduleFilterDTO,
} from "./student.dto";

export class StudentApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/student/me"
  ) {}

  // ============
  // QUERY
  // ============

  async getMyClasses() {
    const res = await this.$api.get<StudentGetClassesResponse>(
      `${this.baseURL}/classes`
    );
    return res.data;
  }

  async getMyAttendance(params?: StudentAttendanceFilterDTO) {
    const res = await this.$api.get<StudentGetAttendanceResponse>(
      `${this.baseURL}/attendance`,
      { params }
    );
    return res.data;
  }

  async getMyGrades(params?: StudentGradesFilterDTO) {
    const res = await this.$api.get<StudentGetGradesResponse>(
      `${this.baseURL}/grades`,
      { params }
    );
    return res.data;
  }

  async getMySchedule(params?: StudentScheduleFilterDTO) {
    const res = await this.$api.get<StudentGetScheduleResponse>(
      `${this.baseURL}/schedule`,
      { params }
    );
    return res.data;
  }
}
