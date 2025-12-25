import { computed } from "vue";
import { usePaginatedFetch } from "~/composables/usePaginatedFetch";
import type { Role } from "~/api/types/enums/role.enum";
import type { AdminGetUserItemData } from "~/api/admin/user/user.dto";
import { adminService } from "~/api/admin";

export function useUsersPaging(
  filters: { value: { roles: Role[]; q: string } },
  setInlineData: (rows: AdminGetUserItemData[]) => void
) {
  const api = adminService();

  const fetchUsers = async (
    filter: { roles: Role[]; q: string },
    page: number,
    pageSize: number,
    signal?: AbortSignal
  ) => {
    const res = await api.user.getUserPage(
      filter.roles,
      page,
      pageSize,
      filter.q,
      signal
    );
    if (!res) {
      throw new DOMException("Canceled", "AbortError");
    }
    const items = res.items ?? [];
    const total = res.total ?? 0;

    setInlineData(items);
    return { items, total };
  };

  const paging = usePaginatedFetch<
    AdminGetUserItemData,
    { roles: Role[]; q: string }
  >(
    fetchUsers,
    1,
    15,
    computed(() => filters.value)
  );

  const isFetching = computed(() => !!paging.loading.value);

  return { ...paging, isFetching };
}
