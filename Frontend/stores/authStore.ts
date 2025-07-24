import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { AuthUser } from "~/types/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(null);
  const user = ref<AuthUser | null>(null);
  // Initialize auth state from localStorage on client side
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
  const login = (newToken: string, userInfo: AuthUser) => {
    console.log("Store login before remove:", userInfo);
    console.log("Store login before remove:", token.value);
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    token.value = newToken;
    user.value = userInfo;
    console.log(token.value);
    console.log("Store login after remove:", userInfo);
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
