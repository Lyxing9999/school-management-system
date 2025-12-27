<script
  setup
  lang="ts"
  generic="R extends Record<string, any>, F extends keyof R = keyof R"
>
import { Edit, Loading } from "@element-plus/icons-vue";
import SaveCancelControls from "~/components/TableEdit/controls/SaveCancelControls.vue";
import { useVModel } from "@vueuse/core";
import type { InlineEditProps } from "~/components/types/tableEdit";
import { debounce } from "lodash-es";
import { validateField } from "~/components/TableEdit/validate/validateField";
import { markRaw, computed, onBeforeUnmount } from "vue";

const props = withDefaults(
  defineProps<
    InlineEditProps<R, F> & { loading?: boolean; disabled?: boolean }
  >(),
  {
    loading: false,
    disabled: false,
    inlineEditActive: false,
    controls: true,
    autoSave: false,
    debounceMs: 300,
    controlsSlot: false,
    customClass: "flex justify-between items-center cursor-pointer",
  }
);

const emit = defineEmits<{
  (e: "update:modelValue", value: R[F]): void;
  (e: "update:inlineEditActive", value: boolean): void;
  (e: "save", row: R, field: F, value: R[F]): void;
  (e: "cancel", row: R, field: F): void;
  (e: "auto-save", row: R, field: F, value: R[F]): void;
}>();

const isBlocked = computed(() => props.loading || props.disabled);

const component = computed(() =>
  props.component ? markRaw(props.component) : null
);
const childComponent = computed(() =>
  props.childComponent ? markRaw(props.childComponent) : null
);

// IMPORTANT: only allow edit mode if there is a component to render
const isEditable = computed(() => !!component.value && !isBlocked.value);

function getFinalValue(): R[F] {
  let val: any = inputValue.value;
  if (props.childComponentProps?.prependValue)
    val = props.childComponentProps.prependValue + val;
  if (props.childComponentProps?.appendValue)
    val = val + props.childComponentProps.appendValue;
  return val as R[F];
}

const inlineEditActive = useVModel(
  props as { inlineEditActive: boolean },
  "inlineEditActive",
  emit,
  { passive: true }
);

const inputValue = computed({
  get: () => {
    const val = props.modelValue ?? props.row[props.field];
    if (props.childComponentProps?.appendValue && val != null) {
      return String(val).replace(props.childComponentProps.appendValue, "");
    }
    return val;
  },
  set: (val: any) => emit("update:modelValue", val as R[F]),
});

function resetInput() {
  emit(
    "update:modelValue",
    (props.modelValue ?? props.row[props.field]) as R[F]
  );
}

function handleSave() {
  if (isBlocked.value) return;

  const error = validateField(inputValue.value, props.rules || []);
  if (error) {
    ElMessage.error(error);
    return;
  }

  const finalValue = getFinalValue();
  emit("update:modelValue", finalValue);
  emit("save", props.row, props.field, finalValue);
  inlineEditActive.value = false;
}

function handleCancel() {
  if (isBlocked.value) return;
  resetInput();
  emit("cancel", props.row, props.field);
  inlineEditActive.value = false;
}

let hasPendingSave = false;

const triggerAutoSave = debounce(() => {
  if (isBlocked.value) return;

  const error = validateField(inputValue.value, props.rules || []);
  if (error) {
    ElMessage.error(error);
    return;
  }

  const finalValue = getFinalValue();
  emit("update:modelValue", finalValue);
  emit("auto-save", props.row, props.field, finalValue);
}, props.debounceMs);

function triggerAutoSaveOnce() {
  if (isBlocked.value) return;
  if (hasPendingSave) return;

  hasPendingSave = true;
  triggerAutoSave();
  setTimeout(() => (hasPendingSave = false), props.debounceMs);
}

function handleChange(value: any) {
  inputValue.value = value;
  if (!props.autoSave) return;
  triggerAutoSaveOnce();
}

function handleBlur() {
  if (!props.autoSave) return;
  if (isBlocked.value) return;

  inlineEditActive.value = false;
  triggerAutoSaveOnce();
}

onBeforeUnmount(() => {
  triggerAutoSave.flush();
});
</script>

<template>
  <!-- VIEW MODE -->
  <div
    v-if="!inlineEditActive"
    :class="[
      props.customClass,
      { 'cursor-not-allowed opacity-60': isBlocked },
      { 'cursor-pointer': isEditable },
    ]"
    @click="isEditable && (inlineEditActive = true)"
  >
    <span class="truncate max-w-[170px] block">
      {{
        Array.isArray(inputValue)
          ? inputValue.slice(0, 3).join(", ") +
            (inputValue.length > 3 ? "..." : "")
          : inputValue || "—"
      }}
    </span>

    <span class="flex items-center space-x-1">
      <el-icon v-if="props.loading" class="is-loading"><Loading /></el-icon>
      <el-icon v-else-if="controls && isEditable"><Edit /></el-icon>
    </span>
  </div>

  <!-- EDIT MODE -->
  <div v-else>
    <component
      v-if="component"
      :is="component"
      v-model="inputValue"
      v-bind="componentProps"
      :disabled="isBlocked"
      @keydown.enter.prevent="handleSave"
      @keydown.esc.prevent="handleCancel"
      @blur="handleBlur"
      @change="handleChange"
    >
      <component
        v-for="opt in childComponentProps?.options || []"
        :is="childComponent"
        :key="opt.value"
        :value="opt.value"
        :label="opt.label"
      />

      <template v-if="controls" #suffix>
        <SaveCancelControls @confirm="handleSave" @cancel="handleCancel" />
      </template>

      <template v-else-if="childComponentProps?.appendValue" #append>
        <span
          v-if="childComponentProps?.appendValue"
          class="px-2 text-gray-500"
        >
          {{ childComponentProps.appendValue }}
        </span>

        <slot
          v-if="controlsSlot"
          name="controlsSlot"
          :row="row"
          :field="field"
        />
      </template>
    </component>

    <!-- Fallback: if edit mode is activated but no component exists, never show blank -->
    <div v-else class="flex items-center justify-between">
      <span class="truncate max-w-[170px] block">
        {{
          Array.isArray(inputValue)
            ? inputValue.slice(0, 3).join(", ") +
              (inputValue.length > 3 ? "..." : "")
            : inputValue || "—"
        }}
      </span>
    </div>
  </div>
</template>
