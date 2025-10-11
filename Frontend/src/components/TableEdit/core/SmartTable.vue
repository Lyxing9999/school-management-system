<script
  lang="ts"
  setup
  generic="T extends Record<string, any> = Record<string, any>"
>
import EditableColumn from "~/components/TableEdit/core/EditableColumn.vue";
import { reactive } from "vue";
import type { ColumnConfig } from "~/components/types/tableEdit";
const props = defineProps<{
  data: T[];
  columns?: ColumnConfig<T>[];
  loading?: boolean;
  smartProps?: Record<string, unknown>;
}>();

const emit = defineEmits<{
  (e: "save", row: T, field: keyof T): void;
  (e: "cancel", row: T, field: keyof T): void;
  (e: "auto-save", row: T, field: keyof T): void;
}>();
const safeColumns = computed(() =>
  (props.columns ?? []).map((c) => reactive({ align: "left", ...c }))
);
defineSlots<{
  operation?: boolean;
  controlsSlot?: boolean;
  append?: boolean;
  prefix?: boolean;
  footer?: boolean;
}>();
const skeletonCount = 5;
</script>
<template>
  <div v-if="props.loading">
    <el-skeleton
      :rows="1"
      animated
      class="table-skeleton-row"
      v-for="i in skeletonCount"
      :key="i"
    />
  </div>
  <div v-else-if="props.data && props.data.length > 0">
    <el-table
      :data="props.data"
      v-bind="props.smartProps"
      :loading="props.loading"
    >
      <EditableColumn
        v-for="(column, colIndex) in safeColumns"
        v-bind="column"
        :key="colIndex"
        :label="column.label"
        :field="column.field as string"
        :component="column.component"
        :componentProps="column.componentProps"
        :childComponent="column.childComponent"
        :childComponentProps="column.childComponentProps"
        :inlineEditActive="column.inlineEditActive"
        :align="column.align as 'left' | 'center' | 'right'"
        :controls="column.controls"
        :controlsSlot="column.controlsSlot"
        :render="column.render"
        :debounceMs="column.debounceMs"
        :autoSave="column.autoSave"
        :operation="column.operation"
        :rules="column.rules"
        :customClass="column.customClass"
        :footer="column.footer"
        @save="(row, field) => emit('save', row as T, field as keyof T)"
        @cancel="(row, field) => emit('cancel', row as T, field as keyof T)"
        @auto-save="(row, field) => emit('auto-save', row as T, field as keyof T)"
      >
        <template v-if="$slots.footer" #footer="slotProps">
          <slot name="footer" v-bind="slotProps" />
        </template>

        <template v-if="$slots.operation" #operation="slotProps">
          <slot name="operation" v-bind="slotProps" />
        </template>
        <template #controlsSlot="slotProps">
          <slot name="controlsSlot" v-bind="slotProps" />
        </template>
      </EditableColumn>
    </el-table>
  </div>
  <div v-else><el-empty /></div>
</template>
