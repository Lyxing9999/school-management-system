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
} from "./dto";

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

  async listAttendanceForClass(classId: string) {
    const res = await this.$api.get<TeacherListClassAttendanceResponse>(
      `${this.baseURL}/classes/${classId}/attendance`
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

  async listGradesForClass(classId: string) {
    const res = await this.$api.get<TeacherListClassGradesResponse>(
      `${this.baseURL}/classes/${classId}/grades`
    );
    return res.data;
  }

  // ----------
  // Schedule
  // ----------

  async listMySchedule() {
    const res = await this.$api.get<TeacherListMyScheduleResponse>(
      `${this.baseURL}/schedule`
    );
    return res.data;
  }
}
