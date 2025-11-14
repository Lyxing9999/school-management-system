import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminCreateClass,
  AdminAssignStudent,
  AdminAssignTeacher,
} from "./dto";
import type { AdminGetClassData } from "~/api/admin/class/dto";
import { ClassApi } from "../class/api";

export class ClassService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private classApi: ClassApi) {}

  async getClassById(id: string) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.getClassById(id)
    );
    return data!;
  }

  async getAllClasses() {
    const { data } = await this.safeApiCall<AdminGetClassData[]>(() =>
      this.classApi.getAllClasses()
    );
    return data!;
  }

  async createClass(classData: AdminCreateClass) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.createClass(classData)
    );
    return data!;
  }

  async updateClass(id: string, classData: AdminCreateClass) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.updateClass(id, classData)
    );
    return data!;
  }

  async softDeleteClass(id: string) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.softDeleteClass(id)
    );
    return data!;
  }

  async assignStudent(id: string, studentData: AdminAssignStudent) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.assignStudent(id, studentData)
    );
    return data!;
  }

  async removeStudent(id: string, studentData: AdminAssignStudent) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.removeStudent(id, studentData)
    );
    return data!;
  }

  async assignTeacher(id: string, teacherData: AdminAssignTeacher) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.assignTeacher(id, teacherData)
    );
    return data!;
  }

  async unassignTeacher(id: string) {
    const { data } = await this.safeApiCall<AdminGetClassData>(() =>
      this.classApi.unassignTeacher(id)
    );
    return data!;
  }
}
