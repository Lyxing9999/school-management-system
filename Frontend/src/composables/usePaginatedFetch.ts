import { ref, unref, type Ref, type ComputedRef } from "vue";

type MaybeRef<T> = Ref<T> | ComputedRef<T>;
import axios from "axios";

export function usePaginatedFetch<T, F>(
  fetchFn: (
    filter: F,
    page: number,
    pageSize: number,
    signal?: AbortSignal
  ) => Promise<{ items: T[]; total: number }>,
  initialPage = 1,
  initialPageSize = 10,
  filter?: MaybeRef<F>
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
      const filterValue = filter
        ? (unref(filter) as F)
        : (undefined as unknown as F);

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
      if (
        err?.name === "AbortError" ||
        err?.name === "CanceledError" ||
        err?.code === "ERR_CANCELED" ||
        axios.isCancel?.(err)
      ) {
        return;
      }

      error.value = err;
      console.error("Fetch failed:", err);
    } finally {
      loading.value = false;
    }
  };

  const goPage = (page: number) => {
    const max = Math.max(Math.ceil(totalRows.value / pageSize.value), 1);
    if (page < 1 || page > max) return;
    fetchPage(page);
  };

  const setPageSize = async (size: number) => {
    pageSize.value = size;
    await fetchPage(1);
  };

  return {
    data,
    loading,
    error,
    currentPage,
    pageSize,
    totalRows,
    fetchPage,
    goPage,
    setPageSize,
  };
}
