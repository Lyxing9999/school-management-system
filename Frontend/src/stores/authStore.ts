// ~/stores/authStore.ts
import { defineStore } from "pinia";
import { computed, ref } from "vue";
import type { UserBaseDataDTO } from "~/api/types/user.dto";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string>("");
  const user = ref<UserBaseDataDTO | null>(null);
  const isReady = ref<boolean>(false);

  const isAuthenticated = computed(() => !!token.value);

  function setToken(next: string) {
    token.value = next;
  }

  function setUser(next: UserBaseDataDTO | null) {
    user.value = next;
  }

  function clear() {
    token.value = "";
    user.value = null;
  }

  function setReady(v: boolean) {
    isReady.value = v;
  }

  return {
    // state
    token,
    user,
    isReady,

    // getters
    isAuthenticated,

    // actions
    setToken,
    setUser,
    clear,
    setReady,
  };
});
