import { ref, type Ref } from "vue";
export function usePaginatedFetch<T, F = undefined>(
  fetchFn: (
    filter: F,
    page: number,
    pageSize: number,
    signal?: AbortSignal
  ) => Promise<{ items: T[]; total: number }>,
  initialPage: number = 1,
  initialPageSize: number = 10,
  filter?: Ref<F>
) {
  const data = ref<T[]>([]);
  const loading = ref(false);
  const error = ref<Error | null>(null);
  const currentPage = ref(initialPage);
  const pageSize = ref(initialPageSize);
  const totalRows = ref(0);
  let controller: AbortController | null = null;
  
  const fetchPage = async (page: number = currentPage.value) => {
    controller?.abort();
    controller = new AbortController();
    loading.value = true;
    error.value = null;

    try {
      const filterValue = filter?.value as F;
      const res = await fetchFn(
        filterValue,
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
    filter,
    currentPage,
    pageSize,
    totalRows,
    fetchPage,
    goPage,
  };
}
