<script
  setup
  lang="ts"
  generic="R extends Record<string, any> = Record<string, any>, F extends keyof R = keyof R"
>
import MultiTypeEditCell from "~/components/TableEdit/core/MultiTypeEditCell.vue";
import RenderCell from "~/components/TableEdit/RenderCell/RenderCellWrapper.vue";
import type { InlineEditColumnProps } from "~/components/types/tableEdit";
const props = defineProps<InlineEditColumnProps<R, F>>();
const emit = defineEmits<{
  (e: "update:modelValue", value: R[F]): void;
  (e: "save", row: R, field: F): void;
  (e: "cancel", row: R, field: F): void;
  (e: "auto-save", row: R, field: F): void;
}>();
defineSlots<{
  default?(props: { row: R; field: F }): any;
  header?(props: { column: { label: string; field: F } }): any;
  footer?(props: { row: R; field: F; value: R[F] }): any;
  operation?(props: { row: R; field: F }): any;
  controlsSlot?(props: { row: R; field: F }): any;
  name?: string;
}>();
</script>

<template>
  <el-table-column
    v-bind="$attrs"
    :label="label"
    :align="align"
    :prop="String(props.field)"
  >
    <template #default="{ row }">
      <template v-if="operation">
        <slot name="operation" :row="row" :field="props.field" />
      </template>
      <template v-else-if="render">
        <RenderCell :vnode="render(row, props.field)" />
      </template>

      <template v-else>
        <MultiTypeEditCell
          :row="row"
          v-model="row[field]"
          :field="field"
          :component="component"
          :componentProps="componentProps"
          :childComponent="childComponent"
          :childComponentProps="childComponentProps"
          :inlineEditActive="inlineEditActive"
          :controls="controls"
          :controlsSlot="controlsSlot"
          :placeholder="placeholder"
          :autoSave="autoSave"
          :rules="rules"
          :debounceMs="debounceMs"
          :customClass="customClass"
          @save="emit('save', row as R, field as F)"
          @cancel="emit('cancel', row as R, field as F)"
          @auto-save="emit('auto-save', row as R, field as F)"
        >
          <template v-if="$slots.footer" #footer>
            <slot name="footer" :row="row" :field="field" :value="row[field]" />
          </template>
          <!-- forward append/prefix if you want -->
          <template v-if="$slots.append" #append>
            <slot name="append" />
          </template>
          <template v-if="$slots.prefix" #prefix>
            <slot name="prefix" />
          </template>
          <template v-if="$slots.controlsSlot" #controlsSlot>
            <slot name="controlsSlot" />
          </template>
        </MultiTypeEditCell>
      </template>
    </template>

    <template #header>
      <slot name="header" :column="{ label: label || '', field: props.field }">
        {{ label }}
      </slot>
    </template>
  </el-table-column>
</template>
