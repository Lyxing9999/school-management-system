import { ref, unref, type Ref, type ComputedRef, watch } from "vue";
import axios from "axios";
import { reportError } from "~/utils/errors/errors";

type MaybeRef<T> = Ref<T> | ComputedRef<T>;

export function usePaginatedFetch<T, F>(
  fetchFn: (
    filter: F,
    page: number,
    pageSize: number,
    signal?: AbortSignal
  ) => Promise<{ items: T[]; total: number }>,
  opts?: {
    initialPage?: number;
    pageSizeRef?: MaybeRef<number>;
    filter?: MaybeRef<F>;
  }
) {
  const data = ref<T[]>([]);
  const error = ref<Error | null>(null);
  const hasFetchedOnce = ref(false);

  const currentPage = ref(opts?.initialPage ?? 1);

  const pageSize = ref<number>(
    opts?.pageSizeRef ? Number(unref(opts.pageSizeRef)) : 10
  );

  const totalRows = ref(0);

  const initialLoading = ref(false);
  const fetching = ref(false);

  let controller: AbortController | null = null;
  let reqId = 0;

  async function fetchPage(page: number = currentPage.value) {
    reqId += 1;
    const myReqId = reqId;

    controller?.abort();
    const myController = new AbortController();
    controller = myController;

    error.value = null;

    if (!hasFetchedOnce.value) initialLoading.value = true;
    else fetching.value = true;

    try {
      const filterValue = opts?.filter
        ? (unref(opts.filter) as F)
        : (undefined as unknown as F);

      const res = await fetchFn(
        filterValue,
        page,
        pageSize.value,
        myController.signal
      );

      if (myReqId !== reqId) return;

      data.value = res.items;
      totalRows.value = res.total;
      currentPage.value = page;
      hasFetchedOnce.value = true;
    } catch (err: any) {
      if (
        err?.name === "AbortError" ||
        err?.name === "CanceledError" ||
        err?.code === "ERR_CANCELED" ||
        axios.isCancel?.(err)
      )
        return;

      if (myReqId !== reqId) return;

      error.value = err;
      reportError(err, "paging.fetchPage", "log");
    } finally {
      if (myReqId === reqId) {
        initialLoading.value = false;
        fetching.value = false;
      }
    }
  }

  function goPage(page: number) {
    const max = Math.max(Math.ceil(totalRows.value / pageSize.value), 1);
    if (page < 1 || page > max) return;
    fetchPage(page);
  }

  async function setPageSize(size: number) {
    pageSize.value = size;
    await fetchPage(1);
  }

  if (opts?.pageSizeRef) {
    watch(
      () => Number(unref(opts.pageSizeRef!)),
      (v) => {
        if (!Number.isFinite(v) || v <= 0) return;
        if (pageSize.value === v) return;

        pageSize.value = v;
        fetchPage(1);
      }
    );
  }

  return {
    data,
    error,
    hasFetchedOnce,
    currentPage,
    pageSize,
    totalRows,
    initialLoading,
    fetching,
    fetchPage,
    goPage,
    setPageSize,
  };
}
