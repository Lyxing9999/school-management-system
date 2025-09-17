import type { AxiosError } from "axios";
import { ref } from "vue";
import { useAuthStore } from "~/stores/authStore";
import { eventBus } from "~/composables/useGlobalEventBus";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import { useMessage } from "~/composables/common/useMessage";

export const useApiUtils = () => {
  const message = useMessage();

  type SafeApiCallOptions = {
    showSuccessNotification?: boolean;
    showErrorNotification?: boolean;
  };

  const safeApiCall = async <T>(
    promise: Promise<ApiResponse<T>>,
    options: SafeApiCallOptions = {}
  ): Promise<{ data: T | null; errors: Record<string, string> }> => {
    const { showSuccessNotification = false, showErrorNotification = false } =
      options;

    let fieldErrors: Record<string, string> = {};

    try {
      const apiRes = await promise;
      if (!apiRes) return { data: null, errors: fieldErrors };

      if (!apiRes.success) {
        if (apiRes.details?.field_errors) {
          fieldErrors = apiRes.details.field_errors;
        }
        if (showErrorNotification) {
          eventBus.emit(
            "error-message",
            apiRes.user_message ||
              apiRes.details?.hint ||
              apiRes.message ||
              "An unexpected error occurred."
          );
        }
        return { data: null, errors: fieldErrors };
      }

      if (showSuccessNotification) {
        message.showSuccess(apiRes.message);
      }

      return { data: apiRes.data ?? null, errors: {} };
    } catch (err) {
      const axiosErr = err as AxiosError<any>;
      const apiErrorData = axiosErr.response?.data as
        | ApiResponse<any>
        | undefined;

      if (apiErrorData?.details?.field_errors) {
        fieldErrors = apiErrorData.details.field_errors;
      }

      // Always throw errors so ErrorBoundary can catch
      if (axiosErr.response?.status === 401) {
        useAuthStore().logout();
        eventBus.emit("session-expired");
        throw axiosErr;
      }

      if (showErrorNotification) {
        eventBus.emit(
          "error-message",
          apiErrorData?.user_message ||
            axiosErr.message ||
            "An unexpected error occurred."
        );
      }

      throw axiosErr;
    }
  };
  return { safeApiCall };
};
