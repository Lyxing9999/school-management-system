import { ref } from "vue";
import { adminService } from "~/api/admin";
import { Status } from "~/api/types/enums/status.enum";
import type { AdminGetUserItemData } from "~/api/admin/user/user.dto";

export function useUserStatusInline() {
  const api = adminService();

  const editingStatusRowId = ref<string | null>(null);
  const statusDraft = ref<Status>(Status.ACTIVE);

  // keep as ref, but update immutably to ensure reactivity is always triggered
  const statusSaving = ref<Record<string, boolean>>({});

  const statusTagType = (s?: Status | string | null) => {
    const v = (s ?? Status.ACTIVE) as Status;
    if (v === Status.ACTIVE) return "success";
    if (v === Status.INACTIVE) return "warning";
    if (v === Status.SUSPENDED) return "danger";
    return "info";
  };

  const formatStatusLabel = (status?: Status | string | number | null) => {
    const s = String(status ?? Status.ACTIVE).trim();
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : "—";
  };

  const startEditStatus = (row: AdminGetUserItemData) => {
    if ((row as any)?.deleted) return;
    editingStatusRowId.value = String(row.id);
    statusDraft.value = (row.status ?? Status.ACTIVE) as Status;
  };

  const cancelEditStatus = () => {
    editingStatusRowId.value = null;
  };

  const saveStatus = async (row: AdminGetUserItemData, nextStatus: Status) => {
    const prev = (row.status ?? Status.ACTIVE) as Status;
    if (prev === nextStatus) return cancelEditStatus();

    const id = String(row.id);

    statusSaving.value = { ...statusSaving.value, [id]: true };
    row.status = nextStatus;

    try {
      await api.user.setUserStatus(id, nextStatus);
    } catch {
      row.status = prev;
    } finally {
      statusSaving.value = { ...statusSaving.value, [id]: false };
      cancelEditStatus();
    }
  };

  return {
    editingStatusRowId,
    statusDraft,
    statusSaving,
    statusTagType,
    formatStatusLabel,
    startEditStatus,
    cancelEditStatus,
    saveStatus,
  };
}
