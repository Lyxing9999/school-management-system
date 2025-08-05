import type { ApiResponse } from "~/types";

export const unwrapApiData = <T>(response: ApiResponse<T> | null): T | null => {
  return response?.data ?? null;
};
