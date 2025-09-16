import { ref, computed } from "vue";
import type { Role } from "~/api/types/enums/role.enum";

export function usePaginatedFetch<T>(
  fetchFn: (
    roles: Role | Role[],
    page: number,
    pageSize: number
  ) => Promise<{ items: T[]; total: number }>,
  initialPage: number = 1,
  initialPageSize: number = 20
) {
  const data = ref<T[]>([]);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  const selectedRoles = ref<Role | Role[]>([]);
  const currentPage = ref(initialPage);
  const pageSize = ref(initialPageSize);
  const totalRows = ref(0);

  const totalPages = computed(() =>
    Math.max(Math.ceil(totalRows.value / pageSize.value), 1)
  );
  const canPrev = computed(() => currentPage.value > 1);
  const canNext = computed(() => currentPage.value < totalPages.value);

  const fetchPage = async (page: number = currentPage.value) => {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetchFn(selectedRoles.value, page, pageSize.value);
      console.log(res);
      data.value = res.items;
      totalRows.value = res.total;
      currentPage.value = page;
    } catch (err: any) {
      error.value = err;
      console.error("Fetch failed:", err);
    } finally {
      loading.value = false;
    }
  };

  const goPage = (page: number) => {
    if (page < 1 || page > totalPages.value) return;
    fetchPage(page);
  };

  const goPrev = () => {
    if (canPrev.value) fetchPage(currentPage.value - 1);
  };
  const goNext = () => {
    if (canNext.value) fetchPage(currentPage.value + 1);
  };
  const setPageSize = (size: number) => {
    pageSize.value = size;
    fetchPage(1);
  };

  return {
    data,
    loading,
    error,
    currentPage,
    selectedRoles,
    pageSize,
    totalRows,
    totalPages,
    canPrev,
    canNext,
    fetchPage,
    goPage,
    goPrev,
    goNext,
    setPageSize,
  };
}
