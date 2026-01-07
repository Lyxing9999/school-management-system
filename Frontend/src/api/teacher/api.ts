// ~/api/teacher/api.ts
import type { AxiosInstance } from "axios";
import type {
  TeacherGetClassesResponse,
  TeacherMarkAttendanceDTO,
  TeacherMarkAttendanceResponse,
  TeacherChangeAttendanceStatusDTO,
  TeacherChangeAttendanceStatusResponse,
  TeacherAddGradeDTO,
  TeacherAddGradeResponse,
  TeacherUpdateGradeScoreDTO,
  TeacherUpdateGradeScoreResponse,
  TeacherChangeGradeTypeDTO,
  TeacherChangeGradeTypeResponse,
  TeacherListClassAttendanceResponse,
  TeacherListClassGradesResponse,
  TeacherStudentsSelectNameListResponse,
  TeacherSubjectsSelectNameListResponse,
  TeacherClassSelectNameListResponse,
  TeacherStudentNameListResponse,
  TeacherListMyScheduleResponse,
  TeacherClassListWithSummeryResponse,
  TeacherSoftDeleteAttendanceResponse,
  TeacherRestoreAttendanceResponse,
  TeacherSoftDeleteGradeResponse,
  TeacherRestoreGradeResponse,
} from "./dto";
export type ListGradesQuery = {
  page?: number;
  page_size?: number;
  term?: string; // "S1" | "S2" | "2025-S1"
  type?: string; // "exam" | "assignment" | ...
  q?: string; // search
  sort?: string; // "-created_at"
};
export class TeacherApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/teacher") {}

  // ----------
  // Classes
  // ----------

  async listMyClasses() {
    const res = await this.$api.get<TeacherGetClassesResponse>(
      `${this.baseURL}/me/classes`
    );
    return res.data;
  }

  async listMyClassesWithSummery() {
    const res = await this.$api.get<TeacherClassListWithSummeryResponse>(
      `${this.baseURL}/me/classes/summary`
    );
    return res.data;
  }

  async listClassNameSelect() {
    const res = await this.$api.get<TeacherClassSelectNameListResponse>(
      `${this.baseURL}/classes/name-select`
    );
    return res.data;
  }
  async listStudentsInClass(classId: string) {
    const res = await this.$api.get<TeacherStudentsSelectNameListResponse>(
      `${this.baseURL}/me/classes/${classId}/students`
    );
    return res.data;
  }
  async listStudentNamesOptionsClass(classId: string) {
    const res = await this.$api.get<TeacherStudentNameListResponse>(
      `${this.baseURL}/me/classes/${classId}/students/name-select`
    );
    return res.data;
  }

  async listSubjectsInClass(classId: string) {
    const res = await this.$api.get<TeacherSubjectsSelectNameListResponse>(
      `${this.baseURL}/me/classes/${classId}/subjects/name-select`
    );
    return res.data;
  }

  // ----------
  // Attendance
  // ----------

  async markAttendance(payload: TeacherMarkAttendanceDTO) {
    const res = await this.$api.post<TeacherMarkAttendanceResponse>(
      `${this.baseURL}/attendance`,
      payload
    );
    return res.data;
  }

  async changeAttendanceStatus(
    attendanceId: string,
    payload: TeacherChangeAttendanceStatusDTO
  ) {
    const res = await this.$api.patch<TeacherChangeAttendanceStatusResponse>(
      `${this.baseURL}/attendance/${attendanceId}/status`,
      payload
    );
    return res.data;
  }

  async listAttendanceForClass(classId: string, params?: { date?: string }) {
    const res = await this.$api.get<TeacherListClassAttendanceResponse>(
      `${this.baseURL}/classes/${classId}/attendance`,
      { params }
    );
    return res.data;
  }
  async softDeleteAttendance(attendanceId: string) {
    const res = await this.$api.delete<TeacherSoftDeleteAttendanceResponse>(
      `${this.baseURL}/attendance/${attendanceId}`
    );
    return res.data;
  }

  async restoreAttendance(attendanceId: string) {
    const res = await this.$api.post<TeacherRestoreAttendanceResponse>(
      `${this.baseURL}/attendance/${attendanceId}/restore`
    );
    return res.data;
  }
  // ----------
  // Grades
  // ----------

  async addGrade(payload: TeacherAddGradeDTO) {
    const res = await this.$api.post<TeacherAddGradeResponse>(
      `${this.baseURL}/grades`,
      payload
    );
    return res.data;
  }

  async updateGradeScore(gradeId: string, payload: TeacherUpdateGradeScoreDTO) {
    const res = await this.$api.patch<TeacherUpdateGradeScoreResponse>(
      `${this.baseURL}/grades/${gradeId}/score`,
      payload
    );
    return res.data;
  }

  async changeGradeType(gradeId: string, payload: TeacherChangeGradeTypeDTO) {
    const res = await this.$api.patch<TeacherChangeGradeTypeResponse>(
      `${this.baseURL}/grades/${gradeId}/type`,
      payload
    );
    return res.data;
  }

  async listGradesForClass(classId: string, query?: ListGradesQuery) {
    const res = await this.$api.get<TeacherListClassGradesResponse>(
      `${this.baseURL}/classes/${classId}/grades`,
      { params: query }
    );
    return res.data;
  }
  async softDeleteGrade(gradeId: string) {
    const res = await this.$api.delete<TeacherSoftDeleteGradeResponse>(
      `${this.baseURL}/grades/${gradeId}`
    );
    return res.data;
  }

  async restoreGrade(gradeId: string) {
    const res = await this.$api.post<TeacherRestoreGradeResponse>(
      `${this.baseURL}/grades/${gradeId}/restore`
    );
    return res.data;
  }
  // ----------
  // Schedule
  // ----------

  async listMySchedule(params?: {
    page?: number;
    page_size?: number;
    class_id?: string;
    day_of_week?: number;
    start_time_from?: string;
    start_time_to?: string;
    signal?: AbortSignal;
  }) {
    const res = await this.$api.get<TeacherListMyScheduleResponse>(
      `${this.baseURL}/schedule`,
      {
        params: {
          page: params?.page,
          page_size: params?.page_size,
          class_id: params?.class_id,
          day_of_week: params?.day_of_week,
          start_time_from: params?.start_time_from,
          start_time_to: params?.start_time_to,
        },
        signal: params?.signal,
      }
    );

    return res.data;
  }
}
