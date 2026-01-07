import type { ApiResponse } from "~/api/types/common/api-response.type";

export const unwrapApiData = <T>(response: ApiResponse<T> | null): T | null => {
  return response?.data ?? null;
};
