import { adminService } from "~/api/admin";
import { ClassStatus } from "~/api/types/enums/class-status.enum";
import type { AdminClassDataDTO } from "~/api/admin/class/class.dto";
import { useInlineStatus } from "~/composables/table-edit/useInlineStatus";

export function useClassSectionStatusInline() {
  const api = adminService();

  return useInlineStatus<AdminClassDataDTO, ClassStatus>(
    async (id, next) => {
      // Return value ignored by useInlineStatus (Promise<unknown> is fine)
      await api.class.setClassStatus(id, next);
    },
    {
      defaultStatus: ClassStatus.ACTIVE,
      isLocked: (row) => Boolean((row as any)?.deleted),

      tagType: (v) => {
        const s = String(v ?? ClassStatus.ACTIVE) as ClassStatus;
        if (s === ClassStatus.ACTIVE) return "success";
        if (s === ClassStatus.INACTIVE) return "warning";
        if (s === ClassStatus.ARCHIVED) return "info";
        return "info";
      },

      label: (v) => {
        const s = String(v ?? ClassStatus.ACTIVE).trim();
        return s ? s.charAt(0).toUpperCase() + s.slice(1) : "—";
      },
    }
  );
}
