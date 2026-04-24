import type { AxiosInstance } from "axios";
import type { ApiResponse } from "~/api/types/common/api-response.type";

import type {
  AttendanceApproveEarlyLeaveDTO,
  AttendanceApproveWrongLocationDTO,
  AttendanceCheckInDTO,
  AttendanceCheckOutDTO,
  AttendanceDTO,
  EarlyLeaveReportParams,
  AttendanceListParams,
  AttendancePaginatedDTO,
  AttendanceTeamListParams,
  AttendanceTodayDTO,
  WrongLocationReportParams,
} from "./dto";

export class AttendanceApi {
  constructor(
    private readonly $api: AxiosInstance,
    private readonly baseURL = "/api/hrms/attendance",
  ) {}

  async checkIn(payload: AttendanceCheckInDTO) {
    const res = await this.$api.post<ApiResponse<AttendanceDTO>>(
      `${this.baseURL}/check-in`,
      payload,
    );
    return res.data;
  }

  async checkOut(payload: AttendanceCheckOutDTO) {
    const res = await this.$api.post<ApiResponse<AttendanceDTO>>(
      `${this.baseURL}/check-out`,
      payload,
    );
    return res.data;
  }

  async reviewWrongLocation(
    attendanceId: string,
    payload: AttendanceApproveWrongLocationDTO,
  ) {
    const res = await this.$api.post<ApiResponse<AttendanceDTO>>(
      `${this.baseURL}/${attendanceId}/wrong-location/review`,
      payload,
    );
    return res.data;
  }

  async reviewEarlyLeave(
    attendanceId: string,
    payload: AttendanceApproveEarlyLeaveDTO,
  ) {
    const res = await this.$api.post<ApiResponse<AttendanceDTO>>(
      `${this.baseURL}/${attendanceId}/early-leave/review`,
      payload,
    );
    return res.data;
  }

  async getMyAttendance(params?: Omit<AttendanceListParams, "employee_id" | "include_deleted" | "deleted_only">) {
    const res = await this.$api.get<ApiResponse<AttendancePaginatedDTO>>(
      `${this.baseURL}/me`,
      { params },
    );
    return res.data;
  }

  async getMyAttendanceToday() {
    const res = await this.$api.get<ApiResponse<AttendanceTodayDTO>>(
      `${this.baseURL}/me/today`,
    );
    return res.data;
  }

  async getAttendances(params?: AttendanceListParams) {
    const res = await this.$api.get<ApiResponse<AttendancePaginatedDTO>>(
      this.baseURL,
      { params },
    );
    return res.data;
  }

  async getTeamAttendances(params?: AttendanceTeamListParams) {
    const res = await this.$api.get<ApiResponse<AttendancePaginatedDTO>>(
      `${this.baseURL}/team`,
      { params },
    );
    return res.data;
  }

  async getWrongLocationReports(params?: WrongLocationReportParams) {
    const res = await this.$api.get<ApiResponse<AttendancePaginatedDTO>>(
      `${this.baseURL}/reports/wrong-location`,
      { params },
    );
    return res.data;
  }

  async getEarlyLeaveReports(params?: EarlyLeaveReportParams) {
    const res = await this.$api.get<ApiResponse<AttendancePaginatedDTO>>(
      `${this.baseURL}/reports/early-leave`,
      { params },
    );
    return res.data;
  }
  
}
