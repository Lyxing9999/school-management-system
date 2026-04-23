import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";

import type {
  LeaveRequestDTO,
  LeaveSubmitDTO,
  LeaveApproveDTO,
  LeaveRejectDTO,
  LeaveRequestListParams,
  LeaveRequestListResponseDTO,
  LeaveSummaryDTO,
  LeaveBalanceDTO,
} from "./dto";

import { LeaveRequestApi } from "./api";

export class LeaveRequestService {
  private readonly callApi = useApiUtils().callApi;

  constructor(private readonly leaveRequestApi: LeaveRequestApi) {}

  /**
   * Submit a new leave request
   * POST /api/hrms/leave-requests
   */
  async submitRequest(
    payload: LeaveSubmitDTO,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestDTO> {
    const data = await this.callApi<LeaveRequestDTO>(
      () => this.leaveRequestApi.submitRequest(payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  /**
   * Get all leave requests
   * GET /api/hrms/leave-requests
   */
  async getRequests(
    params?: LeaveRequestListParams,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestListResponseDTO> {
    const data = await this.callApi<LeaveRequestListResponseDTO>(
      () => this.leaveRequestApi.getRequests(params),
      options,
    );
    return (
      data ?? {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 0,
      }
    );
  }

  // Backward-compatible alias for legacy callers.
  async getAll(
    params?: LeaveRequestListParams,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestListResponseDTO> {
    return this.getRequests(params, options);
  }

  /**
   * Get my leave requests
   * GET /api/hrms/leave-requests/my
   */
  async getMyRequests(
    params?: LeaveRequestListParams,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestListResponseDTO> {
    const data = await this.callApi<LeaveRequestListResponseDTO>(
      () => this.leaveRequestApi.getMyRequests(params),
      options,
    );
    return (
      data ?? {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 0,
      }
    );
  }

  /**
   * Get a specific leave request
   * GET /api/hrms/leave-requests/<leave_id>
   */
  async getRequest(
    id: string,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestDTO> {
    const data = await this.callApi<LeaveRequestDTO>(
      () => this.leaveRequestApi.getRequest(id),
      options,
    );
    return data!;
  }

  /**
   * Get pending leave requests
   * GET /api/hrms/leave-requests/pending-reviews
   */
  async getPendingRequests(
    params?: LeaveRequestListParams,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestListResponseDTO> {
    const data = await this.callApi<LeaveRequestListResponseDTO>(
      () => this.leaveRequestApi.getPendingRequests(params),
      options,
    );
    return (
      data ?? {
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        total_pages: 0,
      }
    );
  }

  /**
   * Get my leave summary
   * GET /api/hrms/leave-requests/my-summary
   */
  async getMySummary(options?: ApiCallOptions): Promise<LeaveSummaryDTO> {
    const data = await this.callApi<LeaveSummaryDTO>(
      () => this.leaveRequestApi.getMySummary(),
      options,
    );
    return (
      data ?? {
        total_requests: 0,
        pending: 0,
        approved: 0,
        rejected: 0,
        cancelled: 0,
        total_approved_days: 0,
      }
    );
  }

  /**
   * Get my leave balance
   * GET /api/hrms/leave-requests/my-balance
   */
  async getMyBalance(options?: ApiCallOptions): Promise<LeaveBalanceDTO> {
    const data = await this.callApi<LeaveBalanceDTO>(
      () => this.leaveRequestApi.getMyBalance(),
      options,
    );
    return (
      data ?? {
        annual_entitlement: 0,
        used_days: 0,
        remaining_days: 0,
      }
    );
  }

  /**
   * Approve a leave request
   * POST /api/hrms/leave-requests/<leave_id>/approve
   */
  async approveRequest(
    id: string,
    payload: LeaveApproveDTO,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestDTO> {
    const data = await this.callApi<LeaveRequestDTO>(
      () => this.leaveRequestApi.approveRequest(id, payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  /**
   * Reject a leave request
   * POST /api/hrms/leave-requests/<leave_id>/reject
   */
  async rejectRequest(
    id: string,
    payload: LeaveRejectDTO,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestDTO> {
    const data = await this.callApi<LeaveRequestDTO>(
      () => this.leaveRequestApi.rejectRequest(id, payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  /**
   * Cancel a leave request
   * POST /api/hrms/leave-requests/<leave_id>/cancel
   */
  async cancelRequest(
    id: string,
    options?: ApiCallOptions,
  ): Promise<LeaveRequestDTO> {
    const data = await this.callApi<LeaveRequestDTO>(
      () => this.leaveRequestApi.cancelRequest(id),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }
}
