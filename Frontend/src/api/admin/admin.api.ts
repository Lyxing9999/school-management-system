import type { AxiosInstance } from "axios";
import type {
  AdminGetPageUserResponse,
  AdminCreateUser,
  AdminCreateClass,
  AdminGetUserResponse,
  AdminUpdateUser,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffResponse,
  AdminGetClassResponse,
  AdminGetTeacherSelectResponse,
  AdminStudentInfoCreate,
  AdminStudentInfoUpdate,
  AdminStudentInfoResponse,
  AdminUpdateClass,
  AdminAssignTeacher,
  AdminUnassignTeacher,
  AdminAssignStudent,
  AdminUnassignStudent,
  AdminGetAllClassesResponse,
  AdminSubjectResponse,
  AdminCreateSubject,
  AdminUpdateSubject,
} from "./admin.dto";
import { Role } from "~/api/types/enums/role.enum";
export class AdminApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/admin") {}

  async getUsers(
    roles: Role | Role[],
    page: number,
    pageSize: number
  ): Promise<AdminGetPageUserResponse> {
    const params = { page, page_size: pageSize } as Record<string, any>;

    if (Array.isArray(roles)) {
      params["role[]"] = roles;
    } else {
      params.role = roles;
    }
    const res = await this.$api.get<AdminGetPageUserResponse>(
      `${this.baseURL}/users`,
      { params }
    );
    return res.data;
  }

  async createUser(userData: AdminCreateUser): Promise<AdminGetUserResponse> {
    const res = await this.$api.post<AdminGetUserResponse>(
      `${this.baseURL}/users`,
      userData
    );
    return res.data;
  }

  async updateUser(
    id: string,
    userData: AdminUpdateUser
  ): Promise<AdminGetUserResponse> {
    const res = await this.$api.patch<AdminGetUserResponse>(
      `${this.baseURL}/users/${id}`,
      userData
    );
    return res.data;
  }

  async deleteUser(id: string): Promise<AdminGetUserResponse> {
    const res = await this.$api.delete<AdminGetUserResponse>(
      `${this.baseURL}/users/${id}`
    );
    return res.data;
  }

  async createStaff(
    staffData: AdminCreateStaff
  ): Promise<AdminGetStaffResponse> {
    const res = await this.$api.post<AdminGetStaffResponse>(
      `${this.baseURL}/staff`,
      staffData
    );
    return res.data;
  }

  async updateStaff(
    id: string,
    staffData: AdminUpdateStaff
  ): Promise<AdminGetStaffResponse> {
    const res = await this.$api.patch<AdminGetStaffResponse>(
      `${this.baseURL}/staff/${id}`,
      staffData
    );
    return res.data;
  }

  async deleteStaff(id: string): Promise<AdminGetStaffResponse> {
    const res = await this.$api.delete<AdminGetStaffResponse>(
      `${this.baseURL}/staff/${id}`
    );
    return res.data;
  }

  async getStaffDetail(id: string): Promise<AdminGetStaffResponse> {
    const res = await this.$api.get<AdminGetStaffResponse>(
      `${this.baseURL}/staff/${id}`
    );
    return res.data;
  }

  async getStudentInfo(id: string): Promise<AdminStudentInfoResponse> {
    const res = await this.$api.get<AdminStudentInfoResponse>(
      `${this.baseURL}/student/${id}`
    );
    return res.data;
  }
  // admin.api.ts
  async updateStudentInfo(
    id: string,
    studentData: AdminStudentInfoUpdate & { photo_file?: File | null }
  ) {
    const formData = new FormData();

    Object.entries(studentData).forEach(([key, value]) => {
      if (value === undefined || value === null || key === "photo_file") return;
      formData.append(
        key,
        Array.isArray(value) ? JSON.stringify(value) : (value as string | Blob)
      );
    });

    if (studentData.photo_file) {
      formData.append("photo_url", studentData.photo_file); // matches backend
    }

    // Debug
    for (const [key, value] of formData.entries()) {
      console.log(key, value);
    }

    const res = await this.$api.patch<AdminStudentInfoResponse>(
      `${this.baseURL}/student/${id}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );

    return res.data;
  }
  async getTeacherSelect(): Promise<AdminGetTeacherSelectResponse> {
    const res = await this.$api.get<AdminGetTeacherSelectResponse>(
      `${this.baseURL}/staff/academic-select`
    );
    return res.data;
  }

  // -------------------------
  // CLASS CRUD
  // -------------------------
  async createClass(
    classData: AdminCreateClass
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.post<AdminGetClassResponse>(
      `${this.baseURL}`,
      classData
    );
    return res.data;
  }

  async updateClass(
    id: string,
    classData: AdminUpdateClass
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.patch<AdminGetClassResponse>(
      `${this.baseURL}/classes/${id}`,
      classData
    );
    return res.data;
  }

  async softDeleteClass(id: string): Promise<AdminGetClassResponse> {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${id}/soft-delete`
    );
    return res.data;
  }

  async getAllClasses(): Promise<AdminGetAllClassesResponse> {
    const res = await this.$api.get<AdminGetAllClassesResponse>(
      `${this.baseURL}/classes`
    );
    return res.data;
  }

  async getClassById(id: string): Promise<AdminGetClassResponse> {
    const res = await this.$api.get<AdminGetClassResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  // -------------------------
  // TEACHER
  // -------------------------
  async assignTeacher(
    id: string,
    data: AdminAssignTeacher
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.patch<AdminGetClassResponse>(
      `${this.baseURL}/${id}/teacher`,
      data
    );
    return res.data;
  }

  async unassignTeacher(id: string): Promise<AdminGetClassResponse> {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${id}/teacher`
    );
    return res.data;
  }

  // -------------------------
  // STUDENTS
  // -------------------------
  async assignStudent(
    id: string,
    data: AdminAssignStudent
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.patch<AdminGetClassResponse>(
      `${this.baseURL}/${id}/students`,
      data
    );
    return res.data;
  }

  async removeStudent(
    id: string,
    data: AdminUnassignStudent
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.delete<AdminGetClassResponse>(
      `${this.baseURL}/${id}/students`,
      { data }
    );
    return res.data;
  }

  // -------------------------
  // SUBJECTS CRUD
  // -------------------------
  async getSubjects(): Promise<AdminSubjectResponse> {
    const res = await this.$api.get<AdminSubjectResponse>(
      `${this.baseURL}/subject`
    );
    return res.data;
  }
  async getSubjectById(id: string): Promise<AdminSubjectResponse> {
    const res = await this.$api.get<AdminSubjectResponse>(
      `${this.baseURL}/subject/${id}`
    );
    return res.data;
  }
  async createSubject(data: AdminCreateSubject): Promise<AdminSubjectResponse> {
    const res = await this.$api.post<AdminSubjectResponse>(
      `${this.baseURL}/subject`,
      data
    );
    return res.data;
  }
  async updateSubject(
    id: string,
    data: AdminUpdateSubject
  ): Promise<AdminSubjectResponse> {
    const res = await this.$api.patch<AdminSubjectResponse>(
      `${this.baseURL}/subject/${id}`,
      data
    );
    return res.data;
  }

  async deleteSubject(id: string): Promise<AdminSubjectResponse> {
    const res = await this.$api.delete<AdminSubjectResponse>(
      `${this.baseURL}/subject/${id}`
    );
    return res.data;
  }
}
