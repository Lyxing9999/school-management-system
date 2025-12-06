//api
import { AuthApi } from "./iam.api";

//service
import { AuthService } from "./iam.service";

let _iamService: ReturnType<typeof createIamService> | null = null;

function createIamService() {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is undefined.");

  const iamApi = {
    auth: new AuthApi($api),
  };

  return {
    auth: new AuthService(iamApi.auth),
  };
}

export const iamService = () => (_iamService ??= createIamService());
