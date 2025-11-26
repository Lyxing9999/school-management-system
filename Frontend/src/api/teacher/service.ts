// ~/api/teacher/service.ts
import { useApiUtils } from "~/utils/useApiUtils";
import { TeacherApi } from "./api";
import type {
  TeacherClassListDTO,
  TeacherAttendanceListDTO,
  TeacherGradeListDTO,
  TeacherMarkAttendanceDTO,
  TeacherChangeAttendanceStatusDTO,
  TeacherAddGradeDTO,
  TeacherUpdateGradeScoreDTO,
  TeacherChangeGradeTypeDTO,
} from "./dto";
import type { AttendanceDTO, GradeDTO } from "~/api/types/school.dto";

export class TeacherService {
  private safeApiCall = useApiUtils().safeApiCall;

  constructor(private teacherApi: TeacherApi) {}

  // ----------
  // Classes
  // ----------

  async getMyClasses() {
    const { data } = await this.safeApiCall<TeacherClassListDTO>(() =>
      this.teacherApi.getMyClasses()
    );
    return data!;
  }

  // ----------
  // Attendance
  // ----------

  async markAttendance(payload: TeacherMarkAttendanceDTO) {
    const { data } = await this.safeApiCall<AttendanceDTO>(() =>
      this.teacherApi.markAttendance(payload)
    );
    return data!;
  }

  async changeAttendanceStatus(
    attendanceId: string,
    payload: TeacherChangeAttendanceStatusDTO
  ) {
    const { data } = await this.safeApiCall<AttendanceDTO>(() =>
      this.teacherApi.changeAttendanceStatus(attendanceId, payload)
    );
    return data!;
  }

  async listAttendanceForClass(classId: string) {
    const { data } = await this.safeApiCall<TeacherAttendanceListDTO>(() =>
      this.teacherApi.listAttendanceForClass(classId)
    );
    return data!;
  }

  // ----------
  // Grades
  // ----------

  async addGrade(payload: TeacherAddGradeDTO) {
    const { data } = await this.safeApiCall<GradeDTO>(() =>
      this.teacherApi.addGrade(payload)
    );
    return data!;
  }

  async updateGradeScore(gradeId: string, payload: TeacherUpdateGradeScoreDTO) {
    const { data } = await this.safeApiCall<GradeDTO>(() =>
      this.teacherApi.updateGradeScore(gradeId, payload)
    );
    return data!;
  }

  async changeGradeType(gradeId: string, payload: TeacherChangeGradeTypeDTO) {
    const { data } = await this.safeApiCall<GradeDTO>(() =>
      this.teacherApi.changeGradeType(gradeId, payload)
    );
    return data!;
  }

  async listGradesForClass(classId: string) {
    const { data } = await this.safeApiCall<TeacherGradeListDTO>(() =>
      this.teacherApi.listGradesForClass(classId)
    );
    return data!;
  }
}
