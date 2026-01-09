import type { AxiosInstance } from "axios";
import { AuthApi } from "./iam.api";
import { AuthService } from "./iam.service";

export function createIamService(api: AxiosInstance) {
  const iamApi = { auth: new AuthApi(api) };
  return { auth: new AuthService(iamApi.auth) };
}

export function useIamService() {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is undefined. Check src/plugins/00.api.ts");
  return createIamService($api as AxiosInstance);
}
