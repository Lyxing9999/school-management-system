// ~/composables/useDialogDynamicWidth.ts
import { computed, toValue, type MaybeRefOrGetter } from "vue";
import type { Field } from "~/components/types/form";

function countLeafFields(fields: Field<any>[]): number {
  let n = 0;
  for (const f of fields ?? []) {
    if ((f as any).row?.length) n += countLeafFields((f as any).row);
    else if ((f as any).key != null) n += 1;
  }
  return n;
}

export function useDialogDynamicWidth(fields: MaybeRefOrGetter<Field<any>[]>) {
  return computed(() => {
    const list = toValue(fields) ?? [];
    if (list.length === 0) return "400px";

    const count = countLeafFields(list);

    if (count <= 4) return "40%";
    if (count <= 8) return "60%";
    if (count <= 12) return "75%";
    return "90%";
  });
}
