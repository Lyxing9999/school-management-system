<script
  setup
  lang="ts"
  generic="R extends Record<string, any> = Record<string, any>, F extends keyof R = keyof R"
>
import MultiTypeEditCell from "~/components/TableEdit/core/MultiTypeEditCell.vue";
import RenderCell from "~/components/TableEdit/RenderCell/RenderCellWrapper.vue";
import type { InlineEditColumnProps } from "~/components/types/tableEdit";

const props = defineProps<
  InlineEditColumnProps<R, F> & {
    isLoading?: (row: R, field: F) => boolean;
    isDisabled?: (row: R, field: F) => boolean;
  }
>();

const emit = defineEmits<{
  (e: "save", row: R, field: F, value: R[F]): void;
  (e: "cancel", row: R, field: F): void;
  (e: "auto-save", row: R, field: F, value: R[F]): void;
}>();

defineSlots<{
  header?(props: { column: { label: string; field: F } }): any;
  operation?(props: { row: R; field: F }): any;
  controlsSlot?(props: { row: R; field: F }): any;

  /** IMPORTANT: allow any dynamic slot name used by SmartTable columns */
  [key: string]: ((props: any) => any) | undefined;
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
      <!-- SLOT MODE (dynamic slot name) -->
      <template v-if="props.useSlot && props.slotName">
        <slot
          :name="props.slotName"
          v-bind="{ row, field: props.field, value: row[props.field] }"
        />
      </template>

      <!-- OPERATION MODE -->
      <template v-else-if="operation">
        <slot name="operation" :row="row" :field="props.field" />
      </template>

      <!-- RENDER FN MODE -->
      <template v-else-if="render">
        <RenderCell :vnode="render(row, props.field)" />
      </template>

      <!-- INLINE EDIT MODE -->
      <template v-else>
        <MultiTypeEditCell
          v-model="row[props.field]"
          :row="row"
          :field="props.field"
          :component="component"
          :componentProps="componentProps"
          :childComponent="childComponent"
          :childComponentProps="childComponentProps"
          :inlineEditActive="inlineEditActive"
          :controls="controls"
          :controlsSlot="!!$slots.controlsSlot"
          :placeholder="placeholder"
          :autoSave="autoSave"
          :rules="rules"
          :debounceMs="debounceMs"
          :customClass="customClass"
          :loading="props.isLoading ? props.isLoading(row as R, props.field as F) : false"
          :disabled="props.isDisabled ? props.isDisabled(row as R, props.field as F) : false"
          @save="(_, __, value) => emit('save', row as R, props.field as F, value as R[F])"
          @cancel="() => emit('cancel', row as R, props.field as F)"
          @auto-save="(_, __, value) => emit('auto-save', row as R, props.field as F, value as R[F])"
        >
          <template v-if="$slots.controlsSlot" #controlsSlot>
            <slot name="controlsSlot" :row="row" :field="props.field" />
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
