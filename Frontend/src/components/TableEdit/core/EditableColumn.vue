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
  footer?(props: { column: { label: string; field: F } }): any;
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
          @save="emit('save', row as R, field as F)"
          @cancel="emit('cancel', row as R, field as F)"
          @auto-save="emit('auto-save', row as R, field as F)"
        >
          <template #controlsSlot="slotProps">
            <slot name="controlsSlot" v-bind="slotProps" />
          </template>
        </MultiTypeEditCell>
      </template>
    </template>

    <template #header>
      <slot name="header" :column="{ label: label || '', field: props.field }">
        {{ label }}
      </slot>
    </template>

    <template #footer>
      <slot
        name="footer"
        :column="{ label: label || '', field: props.field }"
      />
    </template>
  </el-table-column>
</template>
