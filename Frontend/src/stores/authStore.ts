import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type { UserBaseDataDTO } from "~/api/types/user.dto";

export const useAuthStore = defineStore("auth", () => {
  const token = ref("");
  const user = ref<UserBaseDataDTO | null>(null);

  // "bootstrap finished" (not "logged in")
  const isReady = ref(false);

  const isAuthenticated = computed(() => !!token.value);

  function setToken(v: string) {
    token.value = v;
  }
  function setUser(v: UserBaseDataDTO | null) {
    user.value = v;
  }
  function setReady(v: boolean) {
    isReady.value = v;
  }

  function resetForGuest() {
    token.value = "";
    user.value = null;
    isReady.value = true;
  }

  return {
    token,
    user,
    isReady,
    isAuthenticated,
    setToken,
    setUser,
    setReady,
    resetForGuest,
  };
});
