// ~/api/class/service.ts
import type {
  AdminCreateClassDTO,
  AdminClassDataDTO,
  AdminClassListDTO,
  AdminClassNameSelectListDTO,
} from "./dto";
import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import { ClassApi } from "./api";

export class ClassService {
  private callApi = useApiUtils().callApi;

  constructor(private classApi: ClassApi) {}

  // ============
  // QUERY
  // ============

  async getClasses(options?: ApiCallOptions) {
    const data = await this.callApi<AdminClassListDTO>(
      () => this.classApi.getClasses(),
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

  // ============
  // COMMANDS
  // ============

  async createClass(payload: AdminCreateClassDTO, options?: ApiCallOptions) {
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
}
