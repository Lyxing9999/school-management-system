import { computed, watch, type ComputedRef, type Ref } from "vue";
import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import type {
  HrEmployeeDTO,
  HrEmployeeAccountDTO,
} from "~/api/hr_admin/employees/dto";
import { hrmsAdminService } from "~/api/hr_admin";

export type HrEmployeeRow = {
  id: string;
  employee: HrEmployeeDTO;
  account: HrEmployeeAccountDTO | null;
};

type Filter = {
  q?: string;
  hasAccount?: "yes" | "no";
  status?: "active" | "inactive";
};

type MaybeRef<T> = Ref<T> | ComputedRef<T>;

function mapRows(
  items: Array<{
    employee: HrEmployeeDTO;
    account?: HrEmployeeAccountDTO | null;
  }>,
): HrEmployeeRow[] {
  return items
    .map((item) => ({
      id: item.employee.id,
      employee: item.employee,
      account: item.account ?? null,
    }))
    .filter((row) => !!row.employee);
}

export function useHrEmployeePaging(
  filters: MaybeRef<Filter>,
  setRows: (rows: HrEmployeeRow[]) => void,
) {
  const api = hrmsAdminService();

  const paging = usePaginatedFetch<HrEmployeeRow, Filter>(
    async (filter, page, pageSize) => {
      const res = await api.employee.getEmployeesWithAccounts({
        page,
        limit: pageSize,
        q: filter.q,
        with_accounts: true,
      });

      let rows = mapRows(res.items);

      if (filter.status) {
        rows = rows.filter((x) => x.employee.status === filter.status);
      }

      if (filter.hasAccount === "yes") {
        rows = rows.filter((x) => !!x.account);
      }

      if (filter.hasAccount === "no") {
        rows = rows.filter((x) => !x.account);
      }

      return {
        items: rows,
        total: rows.length,
      };
    },
    {
      initialPage: 1,
      filter: filters,
    },
  );

  watch(
    () => paging.data.value,
    (rows) => setRows(rows),
    { immediate: true },
  );

  const isFetching = computed(
    () => paging.initialLoading.value || paging.fetching.value,
  );

  return {
    ...paging,
    isFetching,
    loading: isFetching,
  };
}
