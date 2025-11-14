import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { UserBaseDataDTO } from "~/api/types/user.dto";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(null);
  const user = ref<UserBaseDataDTO | null>(null);
  function initAuth() {
    if (process.client) {
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        user.value = JSON.parse(storedUser);
      }
      const storedToken = localStorage.getItem("token");
      if (storedToken) {
        token.value = storedToken;
      }
    }
  }
  const login = (newToken: string, userInfo: UserBaseDataDTO) => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    token.value = newToken;
    user.value = userInfo;
    localStorage.setItem("token", newToken);
    localStorage.setItem("user", JSON.stringify(userInfo));
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  return {
    token,
    user,
    login,
    logout,
    isAuthenticated: computed(() => !!token.value),
    initAuth,
  };
});
