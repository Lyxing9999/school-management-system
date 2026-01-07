import axios, { type AxiosError } from "axios";
import { useAuthStore } from "~/stores/authStore";
import { eventBus } from "~/composables/system/useGlobalEventBus";
import type { ApiResponse } from "~/api/types/common/api-response.type";
import { useMessage } from "~/composables/common/useMessage";

export type ApiCallOptions = {
  showSuccess?: boolean;
  showError?: boolean;
  signal?: AbortSignal;
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
        if (apiRes.details?.field_errors)
          fieldErrors = apiRes.details.field_errors;

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

      if (axiosErr.response?.status === 401) {
        useAuthStore().resetForGuest();
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
   * Backward-compatible:
   * - supports fn(): Promise<ApiResponse<T>>
   * - supports fn(opts): Promise<ApiResponse<T>>  (use this to pass signal into axios)
   */
  const callApi = async <T>(
    fn:
      | (() => Promise<ApiResponse<T>>)
      | ((opts: ApiCallOptions) => Promise<ApiResponse<T>>),
    options: ApiCallOptions = {}
  ): Promise<T | null> => {
    const { showSuccess = false, showError = true } = options;

    const runner = () => {
      if (fn.length >= 1)
        return (fn as (o: ApiCallOptions) => Promise<ApiResponse<T>>)(options);
      return (fn as () => Promise<ApiResponse<T>>)();
    };

    const { data } = await safeApiCall<T>(runner, {
      showSuccessNotification: showSuccess,
      showErrorNotification: showError,
    });

    return data;
  };

  return { safeApiCall, callApi };
};
