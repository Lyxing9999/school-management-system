import { computed, watch, type ComputedRef, type Ref } from "vue";
import { storeToRefs } from "pinia";

import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { adminService } from "~/api/admin";
import type { Role } from "~/api/types/enums/role.enum";
import type { AdminGetUserItemData } from "~/api/admin/user/user.dto";

import { usePreferencesStore } from "~/stores/preferencesStore";

export type UsersFilter = { roles: Role[]; q: string };
type MaybeRef<T> = Ref<T> | ComputedRef<T>;

export function useUsersPaging(
  filters: MaybeRef<UsersFilter>,
  setInlineData: (rows: AdminGetUserItemData[]) => void
) {
  const api = adminService();

  const prefs = usePreferencesStore();
  const { tablePageSize } = storeToRefs(prefs);

  const fetchUsers = async (
    filter: UsersFilter,
    page: number,
    pageSize: number,
    signal?: AbortSignal
  ): Promise<{ items: AdminGetUserItemData[]; total: number }> => {
    const res = await api.user.getUserPage(
      filter.roles,
      page,
      pageSize,
      filter.q,
      signal
    );

    // If your service returns null/undefined on abort, normalize it
    if (!res) throw new DOMException("Canceled", "AbortError");

    return {
      items: res.items ?? [],
      total: res.total ?? 0,
    };
  };

  const paging = usePaginatedFetch<AdminGetUserItemData, UsersFilter>(
    fetchUsers,
    {
      initialPage: 1,
      pageSizeRef: tablePageSize,
      filter: filters,
    }
  );

  watch(
    () => paging.data.value,
    (rows) => setInlineData(rows),
    { immediate: true }
  );

  // ✅ single loading signal (no flicker from extra flags)
  const isFetching = computed(
    () => paging.initialLoading.value || paging.fetching.value
  );

  return {
    ...paging,
    isFetching,

    loading: isFetching,
  };
}
