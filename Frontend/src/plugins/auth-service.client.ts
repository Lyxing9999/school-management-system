import { AuthService } from "~/api/iam/iam.service";
import { AuthApi } from "~/api/iam/iam.api";

export default defineNuxtPlugin(() => {
  const { $api } = useNuxtApp();

  const authService = new AuthService(new AuthApi($api));

  return {
    provide: { authService },
  };
});
