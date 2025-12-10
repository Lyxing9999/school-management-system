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

const skeletonCount = 5;
</script>

<template>
  <!-- 1. Empty + loading: show skeleton rows -->
  <div v-if="props.loading && (!props.data || props.data.length === 0)">
    <el-skeleton
      v-for="i in skeletonCount"
      :key="i"
      :rows="1"
      animated
      class="table-skeleton-row"
    />
  </div>

  <!-- 2. Has data: show table + overlay while loading -->
  <div v-else v-loading="props.loading">
    <el-table
      :data="props.data"
      v-bind="props.smartProps"
      height="500"
      max-height="500"
    >
      <EditableColumn
        v-for="(column, colIndex) in safeColumns"
        :key="colIndex"
        v-bind="column"
        :align="column.align as 'left' | 'center' | 'right' | undefined"
        :field="column.field as keyof T"
        @save="(row, field) => emit('save', row as T, field as keyof T)"
        @cancel="(row, field) => emit('cancel', row as T, field as keyof T)"
        @auto-save="(row, field) =>
          emit('auto-save', row as T, field as keyof T)"
      >
        <template v-if="column.useSlots" #[column.slotName]="slotProps">
          <slot :name="column.slotName" v-bind="slotProps" />
        </template>

        <template v-if="column.operation" #operation="slotProps">
          <slot name="operation" v-bind="slotProps" />
        </template>

        <template v-if="column.controlsSlot" #controlsSlot="slotProps">
          <slot name="controlsSlot" v-bind="slotProps" />
        </template>
      </EditableColumn>
    </el-table>
  </div>
</template>
