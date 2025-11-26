import type {
  AdminCreateClassDTO,
  AdminClassDataDTO,
  AdminClassListDTO,
} from "./dto";
import { useApiUtils } from "~/utils/useApiUtils";
import { ClassApi } from "./api";

export class ClassService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private classApi: ClassApi) {}

  // ============
  // QUERY
  // ============
  async getClasses() {
    const { data } = await this.safeApiCall<AdminClassListDTO>(
      () => this.classApi.getClasses(),
      {
        showSuccessNotification: false,
      }
    );
    return data!;
  }

  async getClass(classId: string) {
    const { data } = await this.safeApiCall<AdminClassDataDTO>(
      () => this.classApi.getClass(classId),
      {
        showSuccessNotification: false,
      }
    );
    return data!;
  }

  // ============
  // COMMANDS
  // ============

  async createClass(data: AdminCreateClassDTO) {
    const { data: classData } = await this.safeApiCall<AdminClassDataDTO>(() =>
      this.classApi.createClass(data)
    );
    return classData!;
  }

  async softDeleteClass(classId: string) {
    const { data: classData } = await this.safeApiCall<AdminClassDataDTO>(() =>
      this.classApi.softDeleteClass(classId)
    );
    return classData!;
  }

  async assignClassTeacher(classID: string, teacherId: string) {
    const { data: classData } = await this.safeApiCall<AdminClassDataDTO>(() =>
      this.classApi.assignClassTeacher(classID, teacherId)
    );
    return classData!;
  }

  async enrollStudent(classID: string, studentId: string) {
    const { data: classData } = await this.safeApiCall<AdminClassDataDTO>(() =>
      this.classApi.enrollStudent(classID, studentId)
    );
    return classData!;
  }

  async unenrollStudent(classID: string, studentID: string) {
    const { data: classData } = await this.safeApiCall<AdminClassDataDTO>(() =>
      this.classApi.unenrollStudent(classID, studentID)
    );
    return classData!;
  }
}
