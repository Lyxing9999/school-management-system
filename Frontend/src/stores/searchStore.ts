import { defineStore } from "pinia";
import { ref } from "vue";
import type { AxiosInstance } from "axios";

export const useSearchStore = defineStore("search", () => {
  const $api = useNuxtApp().$api as AxiosInstance;
  const params = ref<Record<string, any>>({});
  const history = ref<string[]>([]);
  const query = ref<string>("");
  const list = ref<any[]>([]);
  const role = ref<string>("admin");

  const setSearchQuery = (value: string) => {
    query.value = value;
    addSearchHistory(value);
    fetchList();
  };

  const addSearchHistory = (value: string) => {
    if (!value.trim()) return;
    if (history.value.includes(value)) {
      history.value = [value, ...history.value.filter((v) => v !== value)];
    } else {
      history.value.unshift(value);
      if (history.value.length > 10) {
        history.value.pop();
      }
    }
  };

  const fetchList = async (): Promise<void> => {
    try {
      const response = await $api.post(`/api/${role.value}/users/search-user`, {
        query: query.value,
        page: 1,
        page_size: 10,
      });
      console.log(response.data);
      list.value = response.data?.data || response.data || [];
    } catch (err) {
      console.error("❌ Search API error:", err);
    }
  };

  const clearSearchHistory = () => {
    history.value = [];
  };

  return {
    query,
    params,
    history,
    setSearchQuery,
    addSearchHistory,
    clearSearchHistory,
    fetchList,
    list,
    role,
  };
});
