import type { AxiosError } from "axios";
import { ref } from "vue";
import { useAuthStore } from "~/stores/authStore";
import { eventBus } from "~/composables/useGlobalEventBus";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import { useMessage } from "~/composables/common/useMessage";

export const useApiUtils = () => {
  const fieldErrors = ref<Record<string, string>>({});
  const message = useMessage();

  type SafeApiCallOptions = {
    showSuccessNotification?: boolean;
    showErrorNotification?: boolean;
  };

  const safeApiCall = async <T>(
    promise: Promise<ApiResponse<T>>,
    options: SafeApiCallOptions = {}
  ): Promise<T | null> => {
    const { showSuccessNotification = false, showErrorNotification = false } =
      options;
    fieldErrors.value = {};

    try {
      const apiRes = await promise;
      const data = apiRes.data;
      if (!apiRes) return null;

      if (!apiRes.success) {
        if (apiRes.details?.field_errors) {
          fieldErrors.value = apiRes.details.field_errors;
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
        return null;
      }

      if (showSuccessNotification) {
        message.showSuccess(apiRes.message);
      }

      return data ?? null;
    } catch (err) {
      const axiosErr = err as AxiosError<any>;

      const apiErrorData = axiosErr.response?.data as
        | ApiResponse<any>
        | undefined;
      console.log("this is apiErrorData", apiErrorData);
      if (apiErrorData?.details?.field_errors) {
        fieldErrors.value = apiErrorData.details.field_errors;
      }

      if (axiosErr.response?.status === 401) {
        useAuthStore().logout();
        eventBus.emit("session-expired");
        return null;
      }

      if (showErrorNotification) {
        eventBus.emit(
          "error-message",
          apiErrorData?.user_message ||
            axiosErr.message ||
            "An unexpected error occurred."
        );
      }

      return null;
    }
  };

  return { safeApiCall, fieldErrors };
};
