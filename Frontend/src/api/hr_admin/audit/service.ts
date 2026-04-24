import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";
import type { AuditLogListParams, AuditLogListResponseDTO } from "./dto";
import { AuditLogApi } from "./api";

export class AuditLogService {
  private readonly callApi = useApiUtils().callApi;

  constructor(private readonly auditLogApi: AuditLogApi) {}

  async getLogs(
    params?: AuditLogListParams,
    options?: ApiCallOptions,
  ): Promise<AuditLogListResponseDTO> {
    const data = await this.callApi<AuditLogListResponseDTO>(
      () => this.auditLogApi.listLogs(params),
      options,
    );
    return (
      data ?? {
        items: [],
        total: 0,
        page: 1,
        page_size: 20,
        total_pages: 0,
      }
    );
  }
}
