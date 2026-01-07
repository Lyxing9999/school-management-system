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

  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const el = document.createElement("textarea");
    el.value = text;
    el.style.position = "fixed";
    el.style.opacity = "0";
    document.body.appendChild(el);
    el.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(el);
    return ok;
  }
}
export function useUserResetPassword() {
  const message = useMessage();
  const adminApi = adminService();

  // Record-based loading (matches your other patterns)
  const resetLoading = ref<Record<string, boolean>>({});

  async function handleResetPassword(row: UserResetRow) {
    const key = String(row.id);

    // prevent duplicate click for same row
    if (resetLoading.value[key]) {
      return { ok: false as const, busy: true as const };
    }

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

      if (!res?.reset_link) {
        message.showError("Reset link not returned");
        return { ok: false as const };
      }

      const copied = await copyToClipboard(res.reset_link);

      await ElMessageBox.alert(
        `
  Reset link:
  ${res.reset_link}

  ${copied ? "Copied to clipboard." : "Copy manually."}
          `.trim(),
        "Reset link ready",
        { confirmButtonText: "OK" }
      );

      message.showSuccess(copied ? "Reset link copied" : "Reset link created");
      return { ok: true as const, reset_link: res.reset_link };
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

  return {
    handleResetPassword,
    resetLoading,
  };
}
