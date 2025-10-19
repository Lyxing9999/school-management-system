import { AdminApi } from "~/api/admin/admin.api";
import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminGetUserData,
  AdminGetPageUserData,
  AdminCreateUser,
  AdminUpdateUser,
  AdminCreateClass,
  AdminGetClass,
  AdminFindTeacherSelect,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  AdminStudentInfoUpdate,
  AdminAssignStudent,
  AdminAssignTeacher,
  AdminAssignSubject,
  AdminUnassignSubject,
} from "~/api/admin/admin.dto";
import type { BaseClassDataDTO } from "~/api/types/baseClass";
import { Role } from "~/api/types/enums/role.enum";
import type { BaseStudentInfo } from "~/api/types/baseStudentInfo";
import type { BaseSubject } from "~/api/types/baseSubject";
export class AdminService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private adminApi: AdminApi) {}

  async getUsers(
    roles: Role | Role[],
    page: number,
    pageSize: number,
    options: {
      showSuccessNotification?: boolean;
      showErrorNotification?: boolean;
    } = {}
  ): Promise<AdminGetPageUserData> {
    const { data } = await this.safeApiCall<AdminGetPageUserData>(
      this.adminApi.getUsers(roles, page, pageSize),
      {
        showSuccessNotification: options.showSuccessNotification ?? false,
        showErrorNotification: options.showErrorNotification ?? true,
      }
    );
    return data!;
  }

  async createUser(userData: AdminCreateUser): Promise<AdminGetUserData> {
    const { data } = await this.safeApiCall<AdminGetUserData>(
      this.adminApi.createUser(userData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async updateUser(
    id: string,
    userData: AdminUpdateUser
  ): Promise<AdminGetUserData> {
    const { data } = await this.safeApiCall<AdminGetUserData>(
      this.adminApi.updateUser(id, userData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async deleteUser(id: string) {
    const { data } = await this.safeApiCall(this.adminApi.deleteUser(id), {
      showSuccessNotification: true,
      showErrorNotification: true,
    });
    return data!;
  }
  async createStaff(staffData: AdminCreateStaff) {
    const { data } = await this.safeApiCall<AdminGetStaffData>(
      this.adminApi.createStaff(staffData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async updateStaff(id: string, staffData: AdminUpdateStaff) {
    const { data } = await this.safeApiCall<AdminGetStaffData>(
      this.adminApi.updateStaff(id, staffData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async getStaffDetail(id: string) {
    console.log(this.adminApi.getStaffDetail(id));
    const { data } = await this.safeApiCall<AdminGetStaffData>(
      this.adminApi.getStaffDetail(id),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async getStudentInfo(id: string) {
    const { data } = await this.safeApiCall<BaseStudentInfo>(
      this.adminApi.getStudentInfo(id),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async updateStudentInfo(id: string, studentData: AdminStudentInfoUpdate) {
    const { data } = await this.safeApiCall<BaseStudentInfo>(
      this.adminApi.updateStudentInfo(id, studentData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  // --- Teacher select ---
  async getTeacherSelect() {
    const { data } = await this.safeApiCall<AdminFindTeacherSelect[]>(
      this.adminApi.getTeacherSelect(),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  // --- Class Management ---
  async getClassById(id: string) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.getClassById(id),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async getAllClasses() {
    const { data } = await this.safeApiCall<BaseClassDataDTO[]>(
      this.adminApi.getAllClasses(),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async createClass(classData: AdminCreateClass) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.createClass(classData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async updateClass(id: string, classData: AdminCreateClass) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.updateClass(id, classData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async softDeleteClass(id: string) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.softDeleteClass(id),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async assignStudent(id: string, studentData: AdminAssignStudent) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.assignStudent(id, studentData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async removeStudent(id: string, studentData: AdminAssignStudent) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.removeStudent(id, studentData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async assignTeacher(id: string, teacherData: AdminAssignTeacher) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.assignTeacher(id, teacherData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async unassignTeacher(id: string) {
    const { data } = await this.safeApiCall<BaseClassDataDTO>(
      this.adminApi.unassignTeacher(id),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async getSubjects() {
    const { data } = await this.safeApiCall<BaseSubject>(
      this.adminApi.getSubjects(),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async getSubjectById(id: string) {
    const { data } = await this.safeApiCall<BaseSubject>(
      this.adminApi.getSubjectById(id),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async createSubject(subjectData: AdminAssignSubject) {
    const { data } = await this.safeApiCall<BaseSubject>(
      this.adminApi.createSubject(subjectData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async updateSubject(id: string, subjectData: AdminAssignSubject) {
    const { data } = await this.safeApiCall<BaseSubject>(
      this.adminApi.updateSubject(id, subjectData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async deleteSubject(id: string, subjectData: AdminUnassignSubject) {
    const { data } = await this.safeApiCall<BaseSubject>(
      this.adminApi.deleteSubject(id, subjectData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
}
