<script
  setup
  lang="ts"
  generic="T extends Record<string, any> = Record<string, any>"
>
import { computed, reactive } from "vue";
import EditableColumn from "~/components/TableEdit/core/EditableColumn.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";

const props = defineProps<{
  data: T[];
  columns?: ColumnConfig<T>[];
  loading?: boolean;
  hasFetchedOnce?: boolean;
  smartProps?: Record<string, unknown>;

  /** `${id}:${field}` -> boolean */
  inlineEditLoading: Record<string, boolean>;
}>();

const emit = defineEmits<{
  (e: "save", row: T, field: keyof T, value: any): void;
  (e: "cancel", row: T, field: keyof T): void;
  (e: "auto-save", row: T, field: keyof T, value: any): void;
}>();

const safeColumns = computed(() =>
  (props.columns ?? []).map((c) => reactive({ align: "left", ...c }))
);

const cellKey = (row: any, field: PropertyKey) =>
  `${String(row?.id)}:${String(field)}`;

const isCellSaving = (row: any, field: PropertyKey) =>
  props.inlineEditLoading?.[cellKey(row, field)] ?? false;

/** any saving inside THIS row? */
const isRowSaving = (row: any) => {
  const prefix = `${String(row?.id)}:`;
  return Object.entries(props.inlineEditLoading ?? {}).some(
    ([k, v]) => v && k.startsWith(prefix)
  );
};

/** Disable other cells in the SAME row while one cell is saving */
const isCellDisabled = (row: any, field: PropertyKey) => {
  if (!isRowSaving(row)) return false;
  return !isCellSaving(row, field);
};

const skeletonCount = 5;
const isEmpty = computed(() => (props.data?.length ?? 0) === 0);
const showSkeleton = computed(
  () => !props.hasFetchedOnce && props.loading && isEmpty.value
);

const emptyText = computed(() => {
  if (!props.hasFetchedOnce) return "";
  return props.loading ? "" : "No data";
});
</script>

<template>
  <div v-if="showSkeleton">
    <el-skeleton
      v-for="i in skeletonCount"
      :key="i"
      :rows="1"
      animated
      class="table-skeleton-row"
    />
  </div>

  <div v-else v-loading="props.loading">
    <el-table
      :data="props.data"
      row-key="id"
      :empty-text="emptyText"
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
        :is-loading="(row, field) => isCellSaving(row, field)"
        :is-disabled="(row, field) => isCellDisabled(row, field)"
        @save="(row, field, value) => emit('save', row as T, field as keyof T, value)"
        @cancel="(row, field) => emit('cancel', row as T, field as keyof T)"
        @auto-save="(row, field, value) => emit('auto-save', row as T, field as keyof T, value)"
      >
        <template
          v-if="column.useSlot && column.slotName"
          #[column.slotName]="slotProps"
        >
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
