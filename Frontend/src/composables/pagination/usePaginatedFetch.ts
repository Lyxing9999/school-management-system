import { ref, type Ref } from "vue";
import { Role } from "~/api/types/enums/role.enum";

export function usePaginatedFetch<T>(
  fetchFn: (
    roles: Role[],
    page: number,
    pageSize: number,
    signal?: AbortSignal // <- pass signal to backend-fetch
  ) => Promise<{ items: T[]; total: number }>,
  initialPage: number = 1,
  initialPageSize: number = 20,
  selectedRoles: Ref<Role[]>
) {
  const data = ref<T[]>([]);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  const currentPage = ref(initialPage);
  const pageSize = ref(initialPageSize);
  const totalRows = ref(0);
  let controller: AbortController | null = null;

  const fetchPage = async (page: number = currentPage.value) => {
    // Cancel previous request
    controller?.abort();
    controller = new AbortController();

    loading.value = true;
    error.value = null;

    try {
      const res = await fetchFn(
        selectedRoles.value,
        page,
        pageSize.value,
        controller.signal
      );
      data.value = res.items;
      totalRows.value = res.total;
      currentPage.value = page;
    } catch (err: any) {
      if (err.name !== "AbortError") {
        error.value = err;
        console.error("Fetch failed:", err);
      }
    } finally {
      loading.value = false;
    }
  };

  const goPage = (page: number) => {
    if (
      page < 1 ||
      page > Math.max(Math.ceil(totalRows.value / pageSize.value), 1)
    )
      return;
    fetchPage(page);
  };

  return {
    data,
    loading,
    error,
    selectedRoles,
    currentPage,
    pageSize,
    totalRows,
    fetchPage,
    goPage,
  };
}
