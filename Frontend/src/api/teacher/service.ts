// ~/api/teacher/service.ts
import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
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
  TeacherStudentSelectNameListDTO,
  TeacherSubjectSelectNameListDTO,
  TeacherClassSelectNameListDTO,
  TeacherStudentNameListDTO,
} from "./dto";
import type { AttendanceDTO, GradeDTO } from "~/api/types/school.dto";

export class TeacherService {
  private callApi = useApiUtils().callApi;

  constructor(private teacherApi: TeacherApi) {}

  // ----------
  // Classes
  // ----------

  async listMyClasses(options?: ApiCallOptions) {
    const data = await this.callApi<TeacherClassListDTO>(
      () => this.teacherApi.listMyClasses(),
      options
    );
    return data!;
  }

  async listClassNameSelect(options?: ApiCallOptions) {
    const data = await this.callApi<TeacherClassSelectNameListDTO>(
      () => this.teacherApi.listClassNameSelect(),
      options
    );
    return data!;
  }

  async listStudentsInClass(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<TeacherStudentSelectNameListDTO>(
      () => this.teacherApi.listStudentsInClass(classId),
      options
    );
    return data!;
  }

  async listSubjectsInClass(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<TeacherSubjectSelectNameListDTO>(
      () => this.teacherApi.listSubjectsInClass(classId),
      options
    );
    return data!;
  }

  async listStudentNamesInClass(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<TeacherStudentNameListDTO>(
      () => this.teacherApi.listStudentNamesInClass(classId),
      options
    );
    return data!;
  }

  // ----------
  // Attendance
  // ----------

  async markAttendance(
    payload: TeacherMarkAttendanceDTO,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AttendanceDTO>(
      () => this.teacherApi.markAttendance(payload),
      options
    );
    return data!;
  }

  async changeAttendanceStatus(
    attendanceId: string,
    payload: TeacherChangeAttendanceStatusDTO,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AttendanceDTO>(
      () => this.teacherApi.changeAttendanceStatus(attendanceId, payload),
      options
    );
    return data!;
  }

  async listAttendanceForClass(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<TeacherAttendanceListDTO>(
      () => this.teacherApi.listAttendanceForClass(classId),
      options
    );
    return data!;
  }

  // ----------
  // Grades
  // ----------

  async addGrade(payload: TeacherAddGradeDTO, options?: ApiCallOptions) {
    const data = await this.callApi<GradeDTO>(
      () => this.teacherApi.addGrade(payload),
      options
    );
    return data!;
  }

  async updateGradeScore(
    gradeId: string,
    payload: TeacherUpdateGradeScoreDTO,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<GradeDTO>(
      () => this.teacherApi.updateGradeScore(gradeId, payload),
      options
    );
    return data!;
  }

  async changeGradeType(
    gradeId: string,
    payload: TeacherChangeGradeTypeDTO,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<GradeDTO>(
      () => this.teacherApi.changeGradeType(gradeId, payload),
      options
    );
    return data!;
  }

  async listGradesForClass(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<TeacherGradeListDTO>(
      () => this.teacherApi.listGradesForClass(classId),
      options
    );
    return data!;
  }
}
