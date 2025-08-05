<script
  setup
  lang="ts"
  generic="R extends Record<string, any> = Record<string, any>"
>
import MultiTypeEditCell from "~/components/TableEdit/MultiTypeEditCell.vue";
import {
  defineProps,
  defineEmits,
  computed,
  defineSlots,
  type VNode,
} from "vue";
import type { InputType } from "~/constants/fields/types/Field";
import RenderCell from "~/components/RenderCell/RenderCellWrapper.vue";

const props = defineProps<{
  label: string;
  field: keyof R;
  width?: number | string;
  align?: string;
  placeholder?: string;
  disabled?: boolean;
  isReadOnlyCell?: boolean;
  showSaveCancelControls?: boolean;
  type?: InputType;
  clearable?: boolean;
  showInputField?: boolean;
  render?: (row: R) => VNode;
}>();

const emit = defineEmits<{
  (e: "save", row: R, field: keyof R): void;
  (e: "cancel", row: R, field: keyof R): void;
}>();

const type = computed(() => props.type ?? "string");
const field = computed(() => props.field);
const placeholder = computed(() => props.placeholder ?? "");
const disabled = computed(() => props.disabled ?? false);
const isReadOnly = props.isReadOnlyCell ?? false;
const render = computed(() => props.render ?? null);
const isOperationColumn = computed(() => type.value === "operation");
const clearable = computed(() => props.clearable ?? false);
const showSaveCancelControls = computed(
  () => props.showSaveCancelControls ?? true
);

defineSlots<{
  default?(props: { row: any; field: string }): any;
  header?(props: { column: { label: string; field: string } }): any;
  footer?(props: { column: { label: string; field: string } }): any;
  operation?(props: { row: any; field: string }): any;
}>();
</script>

<template>
  <el-table-column :label="label" :align="align ?? 'left'">
    <template #default="{ row }">
      <template v-if="isOperationColumn && $slots.operation">
        <slot name="operation" :row="row" :field="field as string" />
      </template>

      <template v-else-if="isReadOnly && render != null">
        <!-- Pass the vnode returned by render(row) to RenderCell to display -->
        <RenderCell :vnode="render(row)" />
      </template>

      <template v-else>
        <MultiTypeEditCell
          :default="row[field] as any"
          v-model="row[field]"
          :label="field as string"
          :placeholder="placeholder"
          :disabled="disabled"
          :clearable="clearable"
          :type="type"
          :readonly="isReadOnly"
          :show-save-cancel-controls="showSaveCancelControls"
          :show-input-field="showInputField"
          @save="$emit('save', row, field)"
          @cancel="$emit('cancel', row, field)"
        />
      </template>
    </template>

    <template #header>
      <slot name="header" :column="{ label: label, field: field as string }">
        {{ label }}
      </slot>
    </template>

    <template #footer>
      <slot name="footer" :column="{ label: label, field: field as string }" />
    </template>
  </el-table-column>
</template>
