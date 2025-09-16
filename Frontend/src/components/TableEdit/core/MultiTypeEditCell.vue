<script
  setup
  lang="ts"
  generic="R extends Record<string, any>, F extends keyof R = keyof R"
>
import SaveCancelControls from "~/components/TableEdit/controls/SaveCancelControls.vue";
import { useVModel } from "@vueuse/core";
import { ElInput } from "element-plus";
import type { InlineEditProps } from "~/components/types/tableEdit";
import { debounce } from "lodash-es";
import { validateField } from "~/components/TableEdit/validate/validateField";
import OptionalSlot from "~/components/TableEdit/slots/OptionalSlot.vue";
const props = withDefaults(defineProps<InlineEditProps<R, F>>(), {
  inlineEditActive: false,
  controls: true,
  autoSave: false,
  debounceMs: 300,
  controlsSlot: false,
});
const emit = defineEmits<{
  (e: "update:modelValue", value: R[F]): void;
  (e: "update:inlineEditActive", value: boolean): void;
  (e: "save", row: R, field: F): void;
  (e: "cancel", row: R, field: F): void;
  (e: "auto-save", row: R, field: F): void;
}>();

function getFinalValue(): R[F] {
  let val: any = inputValue.value;

  // Apply prepend
  if (props.childComponentProps?.prependValue) {
    val = props.childComponentProps.prependValue + val;
  }

  // Apply append
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
const inputComponent = computed(() => props.component || ElInput);

const triggerAutoSave = debounce(() => {
  emit("auto-save", props.row, props.field);
}, props.debounceMs);

function handleBlur() {
  if (props.autoSave) {
    const error = validateField(inputValue.value, props.rules || []);
    if (error) {
      ElMessage.error(error);
      return;
    }
    inlineEditActive.value = false;
    triggerAutoSave();
  }
}
onBeforeUnmount(() => {
  triggerAutoSave.flush();
});
</script>
<template>
  <div
    v-if="!inlineEditActive"
    class="flex justify-between items-center cursor-pointer"
    @click="inlineEditActive = true"
  >
    <span class="truncate max-w-[170px] block">
      {{ inputValue || "—" }}
    </span>

    <span v-if="controls" class="flex items-center space-x-1">
      <el-icon><Edit /></el-icon>
    </span>
  </div>

  <div v-else>
    <component
      :is="inputComponent"
      v-model="inputValue"
      v-bind="componentProps"
      @keydown.enter.prevent="handleSave"
      @keydown.esc.prevent="handleCancel"
      @blur="handleBlur"
    >
      <component
        v-for="opt in childComponentProps?.options || []"
        :is="childComponent"
        :key="opt.value"
        :value="opt.value"
        :label="opt.label"
      />
      <template #append v-if="childComponentProps?.slots?.append">
        <OptionalSlot
          slotName="append"
          :row="row"
          :field="field as string"
          :childComponentProps="childComponentProps"
        />
      </template>

      <template #prefix v-if="childComponentProps?.slots?.prefix">
        <OptionalSlot
          slotName="prefix"
          :row="row"
          :field="field as string"
          :childComponentProps="childComponentProps"
        />
      </template>
      <template v-if="controls" #suffix>
        <SaveCancelControls @confirm="handleSave" @cancel="handleCancel" />
      </template>
      <template v-else-if="controlsSlot" #suffix>
        <slot name="controlsSlot" :row="row" :field="field" />
      </template>
    </component>
  </div>
</template>
