// ~/api/class/service.ts
import type {
  AdminCreateClass,
  AdminClassDataDTO,
  AdminClassNameSelectListDTO,
  AdminStudentsInClassSelectDTO,
  AdminUpdateClassRelationsResultDTO,
  AdminUpdateClassRelationsDTO,
  PagedResult,
  SearchStudentsParams,
  AdminStudentSelectDTO,
  AdminClassPaginatedDTO,
  ListClassesParams,
  AdminSubjectSelectListDTO,
} from "./class.dto";
import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";
import { ClassApi } from "./class.api";

export class ClassService {
  private callApi = useApiUtils().callApi;

  constructor(private classApi: ClassApi) {}

  // ============
  // QUERY
  // ============

  async getClasses(params?: ListClassesParams, options?: ApiCallOptions) {
    const data = await this.callApi<AdminClassPaginatedDTO>(
      () => this.classApi.getClasses(params),
      options
    );
    return data!;
  }

  async getClass(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminClassDataDTO>(
      () => this.classApi.getClass(classId),
      options
    );
    return data!;
  }

  async listClassNameSelect() {
    const data = await this.callApi<AdminClassNameSelectListDTO>(() =>
      this.classApi.listClassNameSelect()
    );
    return data!;
  }
  async listStudentsInClass(classID: string) {
    const data = await this.callApi<AdminStudentsInClassSelectDTO>(() =>
      this.classApi.listStudentsInClass(classID)
    );
    return data!;
  }

  async searchStudentsForEnrollmentSelect(
    classID: string,
    params: SearchStudentsParams,
    signal?: AbortSignal
  ): Promise<PagedResult<AdminStudentSelectDTO>> {
    const data = await this.callApi<PagedResult<AdminStudentSelectDTO>>(() =>
      this.classApi.searchStudentsForEnrollmentSelect(classID, params, signal)
    );
    return data!;
  }
  // ============
  // COMMANDS
  // ============

  async createClass(payload: AdminCreateClass, options?: ApiCallOptions) {
    const classData = await this.callApi<AdminClassDataDTO>(
      () => this.classApi.createClass(payload),
      { showSuccess: true, ...(options ?? {}) }
    );
    return classData!;
  }

  async softDeleteClass(classId: string, options?: ApiCallOptions) {
    const classData = await this.callApi<AdminClassDataDTO>(
      () => this.classApi.softDeleteClass(classId),
      { showSuccess: true, ...(options ?? {}) }
    );
    return classData!;
  }

  async assignClassTeacher(
    classId: string,
    teacherId: string,
    options?: ApiCallOptions
  ) {
    const classData = await this.callApi<AdminClassDataDTO>(
      () => this.classApi.assignClassTeacher(classId, teacherId),
      { showSuccess: true, ...(options ?? {}) }
    );
    return classData!;
  }

  async unassignClassTeacher(classId: string, options?: ApiCallOptions) {
    const classData = await this.callApi<AdminClassDataDTO>(
      () => this.classApi.unassignClassTeacher(classId),
      { showSuccess: true, ...(options ?? {}) }
    );
    return classData!;
  }
  async enrollStudent(
    classId: string,
    studentId: string,
    options?: ApiCallOptions
  ) {
    const classData = await this.callApi<AdminClassDataDTO>(
      () => this.classApi.enrollStudent(classId, studentId),
      { showSuccess: true, ...(options ?? {}) }
    );
    return classData!;
  }

  async unenrollStudent(
    classId: string,
    studentId: string,
    options?: ApiCallOptions
  ) {
    const classData = await this.callApi<AdminClassDataDTO>(
      () => this.classApi.unenrollStudent(classId, studentId),
      { showSuccess: true, ...(options ?? {}) }
    );
    return classData!;
  }

  async updateRelations(
    classId: string,
    payload: AdminUpdateClassRelationsDTO,
    options?: ApiCallOptions
  ) {
    const classData = await this.callApi<AdminUpdateClassRelationsResultDTO>(
      () => this.classApi.updateRelations(classId, payload),
      { showSuccess: false, ...(options ?? {}) }
    );
    return classData!;
  }
  async listSubjectsSelectInClass(classId: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminSubjectSelectListDTO>(
      () => this.classApi.listSubjectsSelectInClass(classId),
      options
    );
    return data!;
  }
}
