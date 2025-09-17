// composables/pagination/usePaginatedFetch.ts
import { ref, computed, watch, type Ref } from "vue";
import { Role } from "~/api/types/enums/role.enum";

import {
  roleStaffOptions,
  roleUserOptions,
  roleOptions,
} from "~/utils/constants/roles";

export function usePaginatedFetch<T>(
  fetchFn: (
    roles: Role[],
    page: number,
    pageSize: number
  ) => Promise<{ items: T[]; total: number }>,
  initialPage: number = 1,
  initialPageSize: number = 20,
  isStaffMode: Ref<boolean | undefined>
) {
  const data = ref<T[]>([]);
  const loading = ref(false);
  const error = ref<Error | null>(null);

  // Selected roles (editable even if User/Staff)
  const selectedRoles = ref<Role[]>([Role.STUDENT]);

  // Compute current options for dropdown
  const currentRoleOptions = computed(() => {
    if (isStaffMode.value === true) return roleStaffOptions;
    if (isStaffMode.value === false) return roleUserOptions;
    return roleOptions;
  });

  const currentPage = ref(initialPage);
  const pageSize = ref(initialPageSize);
  const totalRows = ref(0);

  const fetchPage = async (page: number = currentPage.value) => {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetchFn(selectedRoles.value, page, pageSize.value);
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

  watch(selectedRoles, () => fetchPage(1), { deep: true });
  watch(isStaffMode, (mode) => {
    if (mode === true) {
      selectedRoles.value = roleStaffOptions.map((r) => r.value);
    } else if (mode === false) {
      selectedRoles.value = roleUserOptions.map((r) => r.value);
    }
  });
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
    currentRoleOptions,
    isStaffMode,
    currentPage,
    pageSize,
    totalRows,
    fetchPage,
    goPage,
  };
}
