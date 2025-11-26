<script
  setup
  lang="ts"
  generic="R extends Record<string, any>, F extends keyof R = keyof R"
>
import SaveCancelControls from "~/components/TableEdit/controls/SaveCancelControls.vue";
import { useVModel } from "@vueuse/core";
import type { InlineEditProps } from "~/components/types/tableEdit";
import { debounce } from "lodash-es";
import { validateField } from "~/components/TableEdit/validate/validateField";
import { markRaw, computed } from "vue";
const props = withDefaults(defineProps<InlineEditProps<R, F>>(), {
  inlineEditActive: false,
  controls: true,
  autoSave: false,
  debounceMs: 300,
  controlsSlot: false,
  customClass: "flex justify-between items-center cursor-pointer",
});
const emit = defineEmits<{
  (e: "update:modelValue", value: R[F]): void;
  (e: "update:inlineEditActive", value: boolean): void;
  (e: "save", row: R, field: F): void;
  (e: "cancel", row: R, field: F): void;
  (e: "auto-save", row: R, field: F): void;
}>();
let hasPendingSave = false;
function getFinalValue(): R[F] {
  let val: any = inputValue.value;

  if (props.childComponentProps?.prependValue) {
    val = props.childComponentProps.prependValue + val;
  }

  if (props.childComponentProps?.appendValue) {
    val = val + props.childComponentProps.appendValue;
  }
  return val;
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
    if (props.childComponentProps?.appendValue && val) {
      return val.replace(props.childComponentProps.appendValue, "");
    }
    return val;
  },
  set: (val: string) => emit("update:modelValue", val as R[F]),
});
function resetInput() {
  emit("update:modelValue", props.modelValue ?? props.row[props.field]);
}

function handleSave() {
  const finalValue = getFinalValue();
  const error = validateField(inputValue.value, props.rules || []);
  if (error) {
    ElMessage.error(error);
    return;
  }
  emit("update:modelValue", finalValue);
  emit("save", finalValue, props.field);
  inlineEditActive.value = false;
}

function handleCancel() {
  resetInput();

  emit("cancel", props.row, props.field);
  inlineEditActive.value = false;
}

const triggerAutoSave = debounce(() => {
  props.row[props.field] = getFinalValue() as any;
  emit("auto-save", props.row, props.field);
  hasPendingSave = true;
}, props.debounceMs);

function triggerAutoSaveOnce() {
  if (!hasPendingSave) {
    hasPendingSave = true;
    triggerAutoSave();
    setTimeout(() => {
      hasPendingSave = false;
    }, props.debounceMs);
  }
}

function handleBlur() {
  if (props.autoSave) {
    const error = validateField(inputValue.value, props.rules || []);
    if (error) {
      ElMessage.error(error);
      return;
    }
    inlineEditActive.value = false;
    triggerAutoSaveOnce();
  }
}
onBeforeUnmount(() => {
  triggerAutoSave.flush();
});
const component = computed(() =>
  props.component ? markRaw(props.component) : null
);
const childComponent = computed(() =>
  props.childComponent ? markRaw(props.childComponent) : null
);
function handleChange(value: any) {
  inputValue.value = value;
  if (props.autoSave) {
    const error = validateField(inputValue.value, props.rules || []);
    if (error) return;
    triggerAutoSaveOnce();
  }
}
</script>
<template>
  <div
    v-if="!inlineEditActive"
    :class="props.customClass"
    @click="inlineEditActive = true"
  >
    <span class="truncate max-w-[170px] block">
      {{
        Array.isArray(inputValue)
          ? inputValue.slice(0, 3).join(", ") +
            (inputValue.length > 3 ? "..." : "")
          : inputValue || "—"
      }}
    </span>

    <span v-if="controls" class="flex items-center space-x-1">
      <el-icon><Edit /></el-icon>
    </span>
  </div>
  <template v-else-if="!component">
    <span>{{ row[props.field] ?? "—" }}</span>
  </template>
  <div v-else>
    <component
      :is="component"
      v-model="inputValue"
      v-bind="componentProps"
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
  </div>
</template>
