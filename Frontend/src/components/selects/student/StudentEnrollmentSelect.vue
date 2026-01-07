<script setup lang="ts">
import { computed } from "vue";
import RemoteSearchSelect, {
  type RemoteResult,
} from "~/components/selects/base/RemoteSearchSelect.vue";
import { adminService } from "~/api/admin";
import type {
  AdminStudentSelectDTO,
  PagedResult,
  SearchStudentsParams,
} from "~/api/admin/class/class.dto";

const adminApi = adminService();

type StudentValue = string[] | null;

type SelectOption = {
  value: string;
  label: string;
};

const props = defineProps<{
  classId: string;
  modelValue: StudentValue;
  disabled?: boolean;

  /** students already in this class (must NEVER appear in dropdown) */
  preloadedOptions?: SelectOption[];
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: StudentValue): void;
}>();

const innerValue = computed({
  get: () => props.modelValue,
  set: (v) => emit("update:modelValue", v),
});

function toSelectOption(x: AdminStudentSelectDTO): SelectOption {
  return { value: String(x.value), label: String(x.label) };
}

const fetchEligible = async (
  q: string,
  cursor?: string | null,
  signal?: AbortSignal
): Promise<RemoteResult<SelectOption>> => {
  if (!props.classId) return { items: [], nextCursor: null };

  const limit = q.trim() === "" ? 20 : 30;

  const res: PagedResult<AdminStudentSelectDTO> =
    await adminApi.class.searchStudentsForEnrollmentSelect(
      props.classId,
      { q, limit, cursor } satisfies SearchStudentsParams,
      signal
    );

  return {
    items: (res.items ?? []).map(toSelectOption),
    nextCursor: res.nextCursor ?? null,
  };
};

const reloadKey = computed(
  () => `${props.classId}|${(props.preloadedOptions ?? []).length}`
);
</script>

<template>
  <RemoteSearchSelect
    v-model="innerValue"
    :fetcher="fetchEligible"
    :preloaded-options="preloadedOptions"
    :hide-preloaded-in-dropdown="true"
    :reload-key="reloadKey"
    label-key="label"
    value-key="value"
    multiple
    clearable
    :default-limit="20"
    :show-default-on-open="true"
    :prevent-keyboard-remove="true"
    :min-query-length="2"
    :debounce-ms="600"
    empty-label="Type to search"
    no-results-label="No results"
    searching-label="Searching..."
    loading-label="Loading students..."
    :disabled="disabled"
  />
</template>
