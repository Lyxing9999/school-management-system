import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";

import { TeacherApi } from "./api";
import type { ListGradesQuery } from "./api";

import type {
  TeacherClassListDTO,
  TeacherClassSelectNameListDTO,
  TeacherStudentSelectNameListDTO,
  TeacherStudentNameListDTO,
  TeacherSubjectSelectNameListDTO,
  TeacherAttendanceListDTO,
  TeacherMarkAttendanceDTO,
  TeacherChangeAttendanceStatusDTO,
  TeacherGradePagedDTO,
  TeacherAddGradeDTO,
  TeacherUpdateGradeScoreDTO,
  TeacherChangeGradeTypeDTO,
  TeacherScheduleListDTO,
  TeacherClassListWithSummeryDTO,
  TeacherSoftDeleteResultDTO,
  TeacherRestoreResultDTO,
  TeacherScheduleSlotSelectListDTO,
} from "./dto";

import type { AttendanceDTO, GradeDTO } from "~/api/types/school.dto";
import type { ListAttendanceQuery, ScheduleSlotSelectQuery } from "./api";

export class TeacherService {
  private callApi = useApiUtils().callApi;

  constructor(private teacherApi: TeacherApi) {}

  // ----------
  // Classes
  // ----------
  listMyClasses(options?: ApiCallOptions) {
    return this.callApi<TeacherClassListDTO>(
      () => this.teacherApi.listMyClasses(),
      options
    );
  }

  listMyClassesWithSummery(options?: ApiCallOptions) {
    return this.callApi<TeacherClassListWithSummeryDTO>(
      () => this.teacherApi.listMyClassesWithSummery(),
      options
    );
  }

  listClassNameSelect(options?: ApiCallOptions) {
    return this.callApi<TeacherClassSelectNameListDTO>(
      () => this.teacherApi.listClassNameSelect(),
      options
    );
  }

  listStudentsInClass(classId: string, options?: ApiCallOptions) {
    return this.callApi<TeacherStudentSelectNameListDTO>(
      () => this.teacherApi.listStudentsInClass(classId),
      options
    );
  }

  listSubjectsInClass(classId: string, options?: ApiCallOptions) {
    return this.callApi<TeacherSubjectSelectNameListDTO>(
      () => this.teacherApi.listSubjectsInClass(classId),
      options
    );
  }

  listStudentNamesOptionsClass(classId: string, options?: ApiCallOptions) {
    return this.callApi<TeacherStudentNameListDTO>(
      () => this.teacherApi.listStudentNamesOptionsClass(classId),
      options
    );
  }

  // ----------
  // Attendance
  // ----------
  markAttendance(payload: TeacherMarkAttendanceDTO, options?: ApiCallOptions) {
    return this.callApi<AttendanceDTO>(
      () => this.teacherApi.markAttendance(payload),
      options
    );
  }

  changeAttendanceStatus(
    attendanceId: string,
    payload: TeacherChangeAttendanceStatusDTO,
    options?: ApiCallOptions
  ) {
    return this.callApi<AttendanceDTO>(
      () => this.teacherApi.changeAttendanceStatus(attendanceId, payload),
      options
    );
  }

  listAttendanceForClass(
    classId: string,
    params?: ListAttendanceQuery,
    options?: ApiCallOptions
  ) {
    return this.callApi<TeacherAttendanceListDTO>(
      () => this.teacherApi.listAttendanceForClass(classId, params),
      options
    );
  }

  softDeleteAttendance(attendanceId: string, options?: ApiCallOptions) {
    return this.callApi<TeacherSoftDeleteResultDTO>(
      () => this.teacherApi.softDeleteAttendance(attendanceId),
      options
    );
  }

  restoreAttendance(attendanceId: string, options?: ApiCallOptions) {
    return this.callApi<TeacherRestoreResultDTO>(
      () => this.teacherApi.restoreAttendance(attendanceId),
      options
    );
  }

  // ----------
  // Grades
  // ----------
  addGrade(payload: TeacherAddGradeDTO, options?: ApiCallOptions) {
    return this.callApi<GradeDTO>(
      () => this.teacherApi.addGrade(payload),
      options
    );
  }

  updateGradeScore(
    gradeId: string,
    payload: TeacherUpdateGradeScoreDTO,
    options?: ApiCallOptions
  ) {
    return this.callApi<GradeDTO>(
      () => this.teacherApi.updateGradeScore(gradeId, payload),
      options
    );
  }

  changeGradeType(
    gradeId: string,
    payload: TeacherChangeGradeTypeDTO,
    options?: ApiCallOptions
  ) {
    return this.callApi<GradeDTO>(
      () => this.teacherApi.changeGradeType(gradeId, payload),
      options
    );
  }

  listGradesForClass(
    classId: string,
    query?: ListGradesQuery,
    options?: ApiCallOptions
  ) {
    return this.callApi<TeacherGradePagedDTO>(
      () => this.teacherApi.listGradesForClass(classId, query),
      options
    );
  }

  softDeleteGrade(gradeId: string, options?: ApiCallOptions) {
    return this.callApi<TeacherSoftDeleteResultDTO>(
      () => this.teacherApi.softDeleteGrade(gradeId),
      options
    );
  }

  restoreGrade(gradeId: string, options?: ApiCallOptions) {
    return this.callApi<TeacherRestoreResultDTO>(
      () => this.teacherApi.restoreGrade(gradeId),
      options
    );
  }

  // ----------
  // Schedule
  // ----------
  listMySchedule(
    params?: {
      page?: number;
      page_size?: number;
      signal?: AbortSignal;
      class_id?: string;
      day_of_week?: number;
      start_time_from?: string;
      start_time_to?: string;
    },
    options?: ApiCallOptions
  ) {
    return this.callApi<TeacherScheduleListDTO>(
      () => this.teacherApi.listMySchedule(params),
      options
    );
  }

  listScheduleSlotSelect(
    query: ScheduleSlotSelectQuery,
    options?: ApiCallOptions
  ) {
    return this.callApi<TeacherScheduleSlotSelectListDTO>(
      () => this.teacherApi.listScheduleSlotSelect(query),
      options
    );
  }
}
