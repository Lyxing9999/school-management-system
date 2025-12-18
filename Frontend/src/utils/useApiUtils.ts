import axios, { type AxiosError } from "axios";
import { useAuthStore } from "~/stores/authStore";
import { eventBus } from "~/composables/useGlobalEventBus";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import { useMessage } from "~/composables/common/useMessage";

export type ApiCallOptions = {
  showSuccess?: boolean;
  showError?: boolean;
};

export const useApiUtils = () => {
  const message = useMessage();

  type SafeApiCallOptions = {
    showSuccessNotification?: boolean;
    showErrorNotification?: boolean;
  };

  const safeApiCall = async <T>(
    fn: () => Promise<ApiResponse<T>>,
    options: SafeApiCallOptions = {}
  ): Promise<{ data: T | null; errors: Record<string, string> }> => {
    const { showSuccessNotification = true, showErrorNotification = true } =
      options;

    let fieldErrors: Record<string, string> = {};

    try {
      const apiRes = await fn();
      if (!apiRes) return { data: null, errors: fieldErrors };

      if (!apiRes.success) {
        if (apiRes.details?.field_errors) {
          fieldErrors = apiRes.details.field_errors;
        }
        if (showErrorNotification) {
          eventBus.emit(
            "error-message",
            apiRes.user_message ||
              apiRes.message ||
              apiRes.details?.hint ||
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
      if (
        axiosErr.code === "ERR_CANCELED" ||
        (axiosErr as any).name === "CanceledError" ||
        axios.isCancel?.(axiosErr)
      ) {
        return { data: null, errors: {} };
      }
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
            apiErrorData?.message ||
            axiosErr.message ||
            "An unexpected error occurred."
        );
      }

      throw axiosErr;
    }
  };

  /**
   * Higher-level helper used by services.
   * This is your “decorator-like” wrapper around safeApiCall.
   */
  const callApi = async <T>(
    fn: () => Promise<ApiResponse<T>>,
    options: ApiCallOptions = {}
  ): Promise<T | null> => {
    const { showSuccess = false, showError = true } = options;

    const { data } = await safeApiCall<T>(fn, {
      showSuccessNotification: showSuccess,
      showErrorNotification: showError,
    });

    // service can decide whether to `!` or handle null
    return data;
  };

  return { safeApiCall, callApi };
};
