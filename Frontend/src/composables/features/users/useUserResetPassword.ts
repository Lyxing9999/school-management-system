import { ref } from "vue";
import { ElMessageBox } from "element-plus";
import { useMessage } from "~/composables/common/useMessage";
import { adminService } from "~/api/admin";

export type UserResetRow = {
  id: string;
  email: string;
};

type RequestResetResult = {
  reset_link?: string;
  message?: string;
};

async function copyToClipboard(text: string) {
  if (!import.meta.client) return false;

  // Modern clipboard
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // fallback below
  }

  // Fallback copy
  try {
    const el = document.createElement("textarea");
    el.value = text;
    el.setAttribute("readonly", "true");
    el.style.position = "fixed";
    el.style.top = "0";
    el.style.left = "0";
    el.style.opacity = "0";
    document.body.appendChild(el);

    el.focus();
    el.select();
    el.setSelectionRange(0, el.value.length);

    const ok = document.execCommand("copy");
    document.body.removeChild(el);
    return ok;
  } catch {
    return false;
  }
}

export function useUserResetPassword() {
  const message = useMessage();
  const adminApi = adminService();

  const resetLoading = ref<Record<string, boolean>>({});

  async function handleResetPassword(row: UserResetRow) {
    const key = String(row.id);
    if (resetLoading.value[key])
      return { ok: false as const, busy: true as const };

    try {
      await ElMessageBox.confirm(
        `Create reset link for ${row.email}?`,
        "Reset password",
        {
          confirmButtonText: "Create",
          cancelButtonText: "Cancel",
          type: "warning",
        }
      );

      resetLoading.value[key] = true;

      const res = (await adminApi.user.requestPasswordReset(
        row.id
      )) as RequestResetResult;
      const link = res?.reset_link;

      if (!link) {
        message.showError("Reset link not returned");
        return { ok: false as const };
      }

      // Show link + Copy button (copy runs on user click -> reliable)
      await ElMessageBox.confirm(
        `Reset link:\n\n${link}\n\nClick "Copy" to copy it to clipboard.`,
        "Reset link ready",
        {
          confirmButtonText: "Copy",
          cancelButtonText: "Close",
          type: "info",
          closeOnClickModal: false,
          closeOnPressEscape: true,
        }
      );

      const copied = await copyToClipboard(link);
      if (copied) {
        message.showSuccess("Reset link copied");
        return { ok: true as const, reset_link: link, copied: true as const };
      } else {
        message.showError("Copy failed. Please copy manually.");
        return { ok: true as const, reset_link: link, copied: false as const };
      }
    } catch (err: any) {
      if (err === "cancel" || err === "close") {
        return { ok: false as const, cancelled: true as const };
      }
      message.showError("Failed to create reset link");
      return { ok: false as const, cancelled: false as const, error: err };
    } finally {
      resetLoading.value[key] = false;
    }
  }

  return { handleResetPassword, resetLoading };
}
