import type { AxiosInstance } from "axios";
import type {
  AdminGetPageUserResponse,
  AdminCreateUser,
  AdminCreateClass,
  AdminGetUserResponse,
  AdminUpdateUsers,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffResponse,
  AdminGetClassResponse,
  AdminGetTeacherSelectResponse,
  AdminStudentInfoCreate,
  AdminStudentInfoUpdate,
  AdminStudentInfoResponse,
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
      params["role[]"] = roles; // send multiple roles
    } else {
      params.role = roles; // send single role
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
    userData: AdminUpdateUsers
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

  async createClass(
    classData: AdminCreateClass
  ): Promise<AdminGetClassResponse> {
    const res = await this.$api.post<AdminGetClassResponse>(
      `${this.baseURL}/classes`,
      classData
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

  async updateStudentInfo(
    id: string,
    studentData: AdminStudentInfoCreate | AdminStudentInfoUpdate
  ): Promise<AdminStudentInfoResponse> {
    const res = await this.$api.put<AdminStudentInfoResponse>(
      `${this.baseURL}/student/${id}`,
      studentData
    );
    return res.data;
  }

  async getTeacherSelect(): Promise<AdminGetTeacherSelectResponse> {
    const res = await this.$api.get<AdminGetTeacherSelectResponse>(
      `${this.baseURL}/staff/academic-select`
    );
    return res.data;
  }
}
