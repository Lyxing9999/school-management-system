import { ref, computed, watch } from "vue";
import { Role } from "~/api/types/enums/role.enum";
import {
  roleOptions,
  roleStaffOptions,
  roleUserOptions,
} from "~/utils/constants/roles";

export type StaffMode = "default" | "user" | "staff";

export function useUserFilters() {
  const q = ref("");
  const staffMode = ref<StaffMode>("default");
  const selectedRoles = ref<Role[]>([]);

  const currentRoleOptions = computed(() => {
    if (staffMode.value === "staff") return roleStaffOptions;
    if (staffMode.value === "user") return roleUserOptions;
    return roleOptions;
  });

  function rolesFromMode(mode: StaffMode): Role[] {
    if (mode === "staff") return roleStaffOptions.map((r) => r.value);
    if (mode === "user") return roleUserOptions.map((r) => r.value);
    return roleOptions.map((r) => r.value);
  }

  function normalizeSelectedRoles() {
    const allowed = new Set(currentRoleOptions.value.map((o) => o.value));
    const filtered = selectedRoles.value.filter((r) => allowed.has(r));
    selectedRoles.value = filtered.length
      ? filtered
      : rolesFromMode(staffMode.value);
  }

  // v-model helper for OverviewHeader (expects string, not Ref<string>)
  const searchModel = computed<string>({
    get: () => q.value,
    set: (v) => (q.value = v),
  });

  const filters = computed(() => ({
    roles: selectedRoles.value,
    q: q.value.trim(),
  }));

  const isDirty = computed(() => {
    const defaultRoles = rolesFromMode(staffMode.value);
    const sameRoles =
      selectedRoles.value.length === defaultRoles.length &&
      selectedRoles.value.every((r) => defaultRoles.includes(r));

    return q.value.trim() !== "" || staffMode.value !== "default" || !sameRoles;
  });

  function resetAll() {
    q.value = "";
    staffMode.value = "default";
    selectedRoles.value = rolesFromMode("default");
    normalizeSelectedRoles();
  }

  // Optional: auto-normalize when role options set changes
  watch(currentRoleOptions, () => normalizeSelectedRoles());

  return {
    q,
    staffMode,
    selectedRoles,
    currentRoleOptions,
    rolesFromMode,
    normalizeSelectedRoles,
    searchModel,
    filters,
    isDirty,
    resetAll,
  };
}
