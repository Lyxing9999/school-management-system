<script
  lang="ts"
  setup
  generic="T extends Record<string, any> = Record<string, any>"
>
import EditableColumn from "~/components/TableEdit/EditableColumn.vue";
import type { InputType } from "~/constants/fields/types/Field";
import type { ColumnConfig } from "~/constants/fields/types/FieldConfig";
import { computed, defineEmits, defineProps, defineSlots } from "vue";

const props = defineProps<{
  data: T[];
  columns?: ColumnConfig<T>[];
}>();

const emit = defineEmits<{
  (e: "save", row: T, field: keyof T): void;
  (e: "cancel", row: T, field: keyof T): void;
}>();

const safeColumns = computed(() =>
  Array.isArray(props.columns) ? props.columns : []
);
defineSlots<{
  operation?: (props: { row: any; field: string }) => any;
}>();
</script>

<template>
  <el-table :data="data">
    <EditableColumn
      v-for="(column, index) in safeColumns"
      :key="index"
      :label="column.label"
      :field="column.field"
      :type="column.type as InputType"
      :show-save-cancel-controls="column.showSaveCancelControls ?? true"
      :disabled="column.disabled"
      :is-read-only-cell="column.readonly"
      :render="column.render"
      :show-input-field="column.showInputField"
      v-slot:operation="slotProps"
      @save="(row, field) => emit('save', row as T, field as keyof T)"
      @cancel="(row, field) => emit('cancel', row as T, field as keyof T)"
      ><slot name="operation" v-bind="slotProps"
    /></EditableColumn>
  </el-table>
</template>
