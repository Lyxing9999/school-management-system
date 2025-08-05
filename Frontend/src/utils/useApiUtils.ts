import type { AxiosError, AxiosResponse } from "axios";
import { ref } from "vue";
import { useAuthStore } from "~/stores/authStore";
import { eventBus } from "~/composables/useGlobalEventBus";
import type { ApiResponse } from "~/types";
import { ElMessage } from "element-plus";

export const useApiUtils = () => {
  const fieldErrors = ref<Record<string, string>>({});

  const safeApiCall = async <T>(
    promise: Promise<ApiResponse<T>>
  ): Promise<T | null> => {
    fieldErrors.value = {};

    try {
      const res = await promise;

      if (!res) {
        return null;
      }

      if (res.success === false) {
        if (res.details?.field_errors) {
          fieldErrors.value = res.details.field_errors;
        }
        const userMessage =
          res.user_message ||
          res.details?.hint ||
          res.message ||
          "An unexpected error occurred.";
        eventBus.emit("error-message", userMessage);

        return null;
      }
      if (res.success) {
        ElMessage.success(res.message);
        return res.data;
      }
      return null;
    } catch (err) {
      const axiosErr = err as AxiosError<any>;
      const apiErrorData = axiosErr.response?.data;

      if (apiErrorData?.details?.field_errors) {
        fieldErrors.value = apiErrorData.details.field_errors;
      }

      if (axiosErr.response?.status === 401) {
        const authStore = useAuthStore();
        authStore.logout();

        eventBus.emit("session-expired");
        return null;
      }

      const message =
        apiErrorData?.user_message ||
        axiosErr.message ||
        "An unexpected error occurred.";
      eventBus.emit("error-message", message);
      return null;
    }
  };
  return {
    safeApiCall,
    fieldErrors,
  };
};
