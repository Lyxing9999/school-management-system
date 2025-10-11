// ~/composables/useDialogDynamicWidth.ts
import { computed } from "vue";
import type { Field } from "~/components/types/form";

export function useDialogDynamicWidth(fields: Field<any>[]) {
  return computed(() => {
    if (!fields || fields.length === 0) return "400px";

    const count = fields.length;

    if (count <= 4) return "40%"; // very few fields — narrow
    if (count <= 8) return "60%"; // medium forms
    if (count <= 12) return "75%"; // large
    return "90%"; // very big form
  });
}
