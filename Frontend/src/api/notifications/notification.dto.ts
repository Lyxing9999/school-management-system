import type { ApiResponse } from "~/api/types/common/api-response.type";

export type NotificationDTO = {
  id: string;
  user_id: string;
  role: string;
  type: NotifType;
  title: string;
  message?: string | null;
  entity_type?: string | null;
  entity_id?: string | null;
  data?: Record<string, any>;
  read_at?: string | null;
  created_at?: string | null;
};

export type NotificationListDTO = { items: NotificationDTO[] };
export type UnreadCountDTO = { unread: number };

export type NotificationListResponse = ApiResponse<NotificationListDTO>;
export type UnreadCountResponse = ApiResponse<UnreadCountDTO>;
export type OkResponse = ApiResponse<{ ok: boolean }>;

export type NotifType =
  | "CLASS_ASSIGNMENT"
  | "CLASS_UNASSIGNED"
  | "CLASS_ENROLLED"
  | "CLASS_REMOVED"
  | "SCHEDULE_ASSIGNED"
  | "SCHEDULE_UPDATED"
  | "GRADE_PUBLISHED"
  | "ANNOUNCEMENT";
