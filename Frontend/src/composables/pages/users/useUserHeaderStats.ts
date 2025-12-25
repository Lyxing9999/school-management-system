import { computed, type Ref } from "vue";
import { useHeaderState } from "~/composables/useHeaderState";
import type { Role } from "~/api/types/enums/role.enum";

export function useUserHeaderStats(
  totalRows: Ref<number>,
  selectedRoles: Ref<Role[]>
) {
  const totalUsers = computed(() => totalRows.value ?? 0);

  return useHeaderState({
    items: [
      {
        key: "users",
        getValue: () => totalUsers.value,
        singular: "user",
        plural: "users",
        variant: "primary",
        hideWhenZero: false,
      },
      {
        key: "roles",
        getValue: () => selectedRoles.value.length,
        singular: "role",
        plural: "roles",
        suffix: "selected",
        variant: "secondary",
        dotClass: "bg-emerald-500",
        hideWhenZero: true,
      },
    ],
  });
}
