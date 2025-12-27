import { ref, unref, type Ref, type ComputedRef } from "vue";
import axios from "axios";
import { reportError } from "~/utils/errors";
type MaybeRef<T> = Ref<T> | ComputedRef<T>;

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
  const hasFetchedOnce = ref(false);
  const currentPage = ref(initialPage);
  const pageSize = ref(initialPageSize);
  const totalRows = ref(0);

  let controller: AbortController | null = null;
  let reqId = 0;

  const fetchPage = async (page: number = currentPage.value) => {
    reqId += 1;
    const myReqId = reqId;

    controller?.abort();
    const myController = new AbortController();
    controller = myController;

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
        myController.signal
      );

      // ignore stale responses
      if (myReqId !== reqId) return;

      data.value = res.items;
      totalRows.value = res.total;
      currentPage.value = page;
      hasFetchedOnce.value = true;
    } catch (err: any) {
      // ignore aborts/cancels
      if (
        err?.name === "AbortError" ||
        err?.name === "CanceledError" ||
        err?.code === "ERR_CANCELED" ||
        axios.isCancel?.(err)
      ) {
        return;
      }

      // ignore stale errors too
      if (myReqId !== reqId) return;

      error.value = err;

      reportError(err, "paging.fetchPage", "log");
    } finally {
      if (myReqId === reqId) loading.value = false;
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
    hasFetchedOnce,
  };
}
