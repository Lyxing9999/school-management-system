import type { AxiosInstance } from "axios";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { AuditLogListParams, AuditLogListResponseDTO } from "./dto";

export class AuditLogApi {
  constructor(
    private readonly $api: AxiosInstance,
    private readonly baseURL = "/api/hrms/audit-logs",
  ) {}

  async listLogs(params?: AuditLogListParams) {
    const res = await this.$api.get<ApiResponse<AuditLogListResponseDTO>>(
      this.baseURL,
      {
        params: {
          entity_type: params?.entity_type,
          entity_id: params?.entity_id,
          action: params?.action,
          actor_id: params?.actor_id,
          start_at: params?.start_at,
          end_at: params?.end_at,
          include_deleted: params?.include_deleted,
          page: params?.page,
          limit: params?.limit,
        },
        signal: params?.signal,
      },
    );
    return res.data;
  }
}
