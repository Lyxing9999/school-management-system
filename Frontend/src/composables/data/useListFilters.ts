import { computed, ref } from "vue";
import type { StaffMode } from "~/components/filters/StaffModePills.vue";

export function useListFilters() {
  const q = ref("");
  const staffMode = ref<StaffMode>("default");

  const isDirty = computed(
    () => q.value.trim() !== "" || staffMode.value !== "default"
  );

  function reset() {
    q.value = "";
    staffMode.value = "default";
  }

  return { q, staffMode, isDirty, reset };
}
