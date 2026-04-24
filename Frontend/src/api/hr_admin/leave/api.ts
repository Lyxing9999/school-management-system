import type { AxiosInstance } from "axios";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type {
  LeaveRequestDTO,
  LeaveSubmitDTO,
  LeaveApproveDTO,
  LeaveRejectDTO,
  LeaveRequestListParams,
  LeaveRequestListResponseDTO,
  LeaveSummaryDTO,
  LeaveBalanceDTO,
  LeaveBalanceListParams,
  LeaveBalanceListResponseDTO,
} from "./dto";

export class LeaveRequestApi {
  constructor(
    private readonly $api: AxiosInstance,
    private readonly baseURL = "/api/hrms/leave-requests",
  ) {}

  /**
   * Submit a new leave request
   * POST /api/hrms/leave-requests
   */
  async submitRequest(payload: LeaveSubmitDTO) {
    const res = await this.$api.post<ApiResponse<LeaveRequestDTO>>(
      this.baseURL,
      payload,
    );
    return res.data;
  }

  /**
   * Get all leave requests with pagination
   * GET /api/hrms/leave-requests
   */
  async getRequests(params?: LeaveRequestListParams) {
    const res = await this.$api.get<ApiResponse<LeaveRequestListResponseDTO>>(
      this.baseURL,
      {
        params: {
          page: params?.page,
          limit: params?.limit,
          employee_id: params?.employee_id,
          status: params?.status,
          start_date: params?.start_date,
          end_date: params?.end_date,
          include_deleted: params?.include_deleted,
          deleted_only: params?.deleted_only,
        },
        signal: params?.signal,
      },
    );
    return res.data;
  }

  // Legacy alias for older callers
  async getAll(params?: LeaveRequestListParams) {
    return this.getRequests(params);
  }

  /**
   * Get my leave requests
   * GET /api/hrms/leave-requests/my
   */
  async getMyRequests(params?: LeaveRequestListParams) {
    const res = await this.$api.get<ApiResponse<LeaveRequestListResponseDTO>>(
      `${this.baseURL}/my`,
      {
        params: {
          page: params?.page,
          limit: params?.limit,
          status: params?.status,
          start_date: params?.start_date,
          end_date: params?.end_date,
        },
        signal: params?.signal,
      },
    );
    return res.data;
  }

  /**
   * Get a specific leave request by ID
   * GET /api/hrms/leave-requests/<leave_id>
   */
  async getRequest(id: string) {
    const res = await this.$api.get<ApiResponse<LeaveRequestDTO>>(
      `${this.baseURL}/${id}`,
    );
    return res.data;
  }

  /**
   * Get pending leave requests awaiting review
   * GET /api/hrms/leave-requests/pending-reviews
   */
  async getPendingRequests(params?: LeaveRequestListParams) {
    const res = await this.$api.get<ApiResponse<LeaveRequestListResponseDTO>>(
      `${this.baseURL}/pending-reviews`,
      {
        params: {
          page: params?.page,
          limit: params?.limit,
          employee_id: params?.employee_id,
          status: params?.status,
          start_date: params?.start_date,
          end_date: params?.end_date,
        },
        signal: params?.signal,
      },
    );
    return res.data;
  }

  /**
   * Get my leave summary
   * GET /api/hrms/leave-requests/my-summary
   */
  async getMySummary() {
    const res = await this.$api.get<ApiResponse<LeaveSummaryDTO>>(
      `${this.baseURL}/my-summary`,
    );
    return res.data;
  }

  /**
   * Get my leave balance
   * GET /api/hrms/leave-requests/my-balance
   */
  async getMyBalance() {
    const res = await this.$api.get<ApiResponse<LeaveBalanceDTO>>(
      `${this.baseURL}/my-balance`,
    );
    return res.data;
  }

  /**
   * Get leave balances by employee
   * GET /api/hrms/leave-requests/balances
   */
  async getBalances(params?: LeaveBalanceListParams) {
    const res = await this.$api.get<
      ApiResponse<LeaveBalanceListResponseDTO>
    >(`${this.baseURL}/balances`, {
      params: {
        page: params?.page,
        limit: params?.limit,
        q: params?.q,
        employee_id: params?.employee_id,
      },
      signal: params?.signal,
    });
    return res.data;
  }

  /**
   * Approve a leave request
   * POST /api/hrms/leave-requests/<leave_id>/approve
   */
  async approveRequest(id: string, payload: LeaveApproveDTO) {
    const res = await this.$api.post<ApiResponse<LeaveRequestDTO>>(
      `${this.baseURL}/${id}/approve`,
      payload,
    );
    return res.data;
  }

  /**
   * Reject a leave request
   * POST /api/hrms/leave-requests/<leave_id>/reject
   */
  async rejectRequest(id: string, payload: LeaveRejectDTO) {
    const res = await this.$api.post<ApiResponse<LeaveRequestDTO>>(
      `${this.baseURL}/${id}/reject`,
      payload,
    );
    return res.data;
  }

  /**
   * Cancel a leave request
   * POST /api/hrms/leave-requests/<leave_id>/cancel
   */
  async cancelRequest(id: string) {
    const res = await this.$api.post<ApiResponse<LeaveRequestDTO>>(
      `${this.baseURL}/${id}/cancel`,
      {},
    );
    return res.data;
  }
}
