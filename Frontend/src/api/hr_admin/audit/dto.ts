import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export interface AuditLogDTO {
  id: string;
  entity_type: string;
  entity_id: string;
  entity_name?: string | null;
  action: string;
  actor_id?: string | null;
  actor_name?: string | null;
  actor_email?: string | null;
  action_at: string;
  details?: Record<string, unknown>;
  lifecycle: LifecycleDTO;
}

export interface AuditLogListParams {
  entity_type?: string;
  entity_id?: string;
  action?: string;
  actor_id?: string;
  start_at?: string;
  end_at?: string;
  include_deleted?: boolean;
  page?: number;
  limit?: number;
  signal?: AbortSignal;
}

export interface AuditLogListResponseDTO {
  items: AuditLogDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
