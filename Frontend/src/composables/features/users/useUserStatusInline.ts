import { adminService } from "~/api/admin";
import { Status } from "~/api/types/enums/status.enum";
import type { AdminGetUserItemData } from "~/api/admin/user/user.dto";
import { useInlineStatus } from "~/composables/table-edit/useInlineStatus";

export function useUserStatusInline() {
  const api = adminService();

  return useInlineStatus<AdminGetUserItemData, Status>(
    (id, next) => api.user.setUserStatus(id, next),
    {
      defaultStatus: Status.ACTIVE,
      isLocked: (row) => Boolean((row as any)?.deleted),

      tagType: (s) => {
        if (s === Status.ACTIVE) return "success";
        if (s === Status.INACTIVE) return "warning";
        if (s === Status.SUSPENDED) return "danger";
        return "info";
      },

      label: (s) => {
        const v = String(s ?? Status.ACTIVE).trim();
        return v ? v.charAt(0).toUpperCase() + v.slice(1) : "—";
      },
    }
  );
}
