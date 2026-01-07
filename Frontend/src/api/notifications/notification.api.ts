import type { AxiosInstance } from "axios";
import type {
  NotificationListResponse,
  UnreadCountResponse,
  OkResponse,
} from "./notification.dto";
import type { NotifType } from "./notification.dto";
type ListLatestParams = {
  limit?: number;
  type?: NotifType;
  unread_only?: boolean;
};

type UnreadCountParams = {
  type?: NotifType;
};

export class NotificationApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api") {}

  async listLatest(params: ListLatestParams = {}) {
    const { limit = 30, type, unread_only } = params;

    return this.$api
      .get<NotificationListResponse>(`${this.baseURL}/notifications`, {
        params: {
          limit,
          type: type || undefined,
          unread_only: unread_only ? 1 : undefined,
        },  
      })
      .then((r) => r.data);
  }

  async unreadCount(params: UnreadCountParams = {}) {
    const { type } = params;

    return this.$api
      .get<UnreadCountResponse>(`${this.baseURL}/notifications/unread-count`, {
        params: { type: type || undefined },
      })
      .then((r) => r.data);
  }

  async markRead(id: string) {
    return this.$api
      .post<OkResponse>(`${this.baseURL}/notifications/${id}/read`)
      .then((r) => r.data);
  }

  async markAllRead(type?: NotifType) {
    return this.$api
      .post<OkResponse>(`${this.baseURL}/notifications/read-all`, null, {
        params: { type: type || undefined },
      })
      .then((r) => r.data);
  }

  async test() {
    return this.$api
      .post<OkResponse>(`${this.baseURL}/notifications/test`)
      .then((r) => r.data);
  }
}
