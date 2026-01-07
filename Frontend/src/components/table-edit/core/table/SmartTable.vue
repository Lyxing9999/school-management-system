<script
  setup
  lang="ts"
  generic="T extends Record<string, any> = Record<string, any>"
>
import { computed, reactive } from "vue";
import { useMediaQuery } from "@vueuse/core";
import EditableColumn from "~/components/table-edit/core/columns/EditableColumn.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";

const props = defineProps<{
  data: T[];
  columns?: ColumnConfig<T>[];
  loading?: boolean;
  hasFetchedOnce?: boolean;
  smartProps?: Record<string, unknown>;
  inlineEditLoading?: Record<string, boolean>;
}>();

const emit = defineEmits<{
  (e: "save", row: T, field: keyof T, value: any): void;
  (e: "cancel", row: T, field: keyof T): void;
  (e: "auto-save", row: T, field: keyof T, value: any): void;
}>();

/** ------------------ Mobile helpers ------------------ */
const isMobile = useMediaQuery("(max-width: 767px)");

/** Merge Element Plus table props with mobile-safe defaults (only if not provided) */
const mergedSmartProps = computed(() => {
  const sp = (props.smartProps ?? {}) as Record<string, any>;

  return {
    ...sp,
    // allow horizontal overflow on mobile (Element Plus default fit=true tends to compress)
    fit: sp.fit ?? (isMobile.value ? false : undefined),
    // let minWidth/content decide widths on mobile
    "table-layout": sp["table-layout"] ?? (isMobile.value ? "auto" : undefined),
  };
});

/** Columns: keep original typing, but disable fixed columns on mobile */
const safeColumns = computed<ColumnConfig<T>[]>(() =>
  (props.columns ?? []).map((c) => {
    const col = reactive({ align: "left", ...c }) as ColumnConfig<T> & {
      fixed?: any;
    };

    // fixed columns often break swipe scroll on mobile
    if (isMobile.value && (col as any).fixed) {
      delete (col as any).fixed;
    }

    return col;
  })
);

/** ------------------ Inline edit state helpers ------------------ */
const cellKey = (row: any, field: PropertyKey) =>
  `${String(row?.id)}:${String(field)}`;

const isCellSaving = (row: any, field: PropertyKey) =>
  props.inlineEditLoading?.[cellKey(row, field)] ?? false;

const isRowSaving = (row: any) => {
  const prefix = `${String(row?.id)}:`;
  return Object.entries(props.inlineEditLoading ?? {}).some(
    ([k, v]) => v && k.startsWith(prefix)
  );
};

const isCellDisabled = (row: any, field: PropertyKey) => {
  if (!isRowSaving(row)) return false;
  return !isCellSaving(row, field);
};

/** ------------------ Empty / Skeleton ------------------ */
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
    <!-- Mobile-safe horizontal scroll -->
    <div class="smart-table-x">
      <el-table
        :data="props.data"
        row-key="id"
        :empty-text="emptyText"
        v-bind="mergedSmartProps"
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

          <template v-if="column.revertSlots" #revertSlots="slotProps">
            <slot name="revertSlots" v-bind="slotProps" />
          </template>
        </EditableColumn>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.smart-table-x {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x pan-y;
}

/* Helps iOS scrolling inside Element Plus table wrapper */
:deep(.el-table__body-wrapper) {
  -webkit-overflow-scrolling: touch;
}
</style>
