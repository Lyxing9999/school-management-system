// ~/composables/common/useLabelMap.ts
import { computed, type Ref } from "vue";

type Option = { value: string; label: string };

export function useLabelMap(options: Ref<Option[]>) {
  return computed<Record<string, string>>(() =>
    options.value.reduce((acc, opt) => {
      acc[opt.value] = opt.label;
      return acc;
    }, {} as Record<string, string>)
  );
}
