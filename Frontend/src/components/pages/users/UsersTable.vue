<script setup lang="ts">
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import ActionButtons from "~/components/table-edit/button/ActionButtons.vue";
import type {
  AdminGetUserItemData,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";
import { Status } from "~/api/types/enums/status.enum";
import InlineStatusCell from "~/components/table-edit/cells/InlineStatusCell.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";

type Row = AdminGetUserItemData;
type RowField = keyof Row;
type EditableField = Extract<keyof AdminGetUserItemData, keyof AdminUpdateUser>;

const props = defineProps<{
  rows: Row[];
  columns: ColumnConfig<Row>[];
  loading: boolean;
  inlineEditLoading: Record<string | number, boolean>;
  hasFetchedOnce: boolean;

  getPreviousValue: (row: Row, field: EditableField) => string;
  editingStatusRowId: string | null;
  statusDraft: Status;
  statusTagType: (s?: Status | string | null | undefined) => any;
  formatStatusLabel: (s?: string | null | undefined) => string;
  statusSaving: Record<string, boolean>;
}>();

const emit = defineEmits<{
  (e: "save", row: Row, field: EditableField): void;
  (e: "cancel", row: Row): void;
  (e: "auto-save", row: Row, field: EditableField): void;
  (e: "revert-field", row: Row, field: EditableField): void;

  (e: "start-edit-status", row: Row): void;
  (e: "cancel-edit-status"): void;
  (e: "save-status", row: Row, val: any): void;
  (e: "update-status-draft", val: any): void;
}>();

function asEditable(field: RowField): EditableField | null {
  if (field === "id") return null;
  return field as EditableField;
}
const statusOptions = [
  { label: "Active", value: Status.ACTIVE },
  { label: "Inactive", value: Status.INACTIVE },
  { label: "Suspended", value: Status.SUSPENDED },
];
import { applyInlineEditMode } from "~/utils/table/applyInlineEditMode";
import { usePreferencesStore } from "~/stores/preferencesStore";

const prefs = usePreferencesStore();

const resolvedUserColumns = computed(() =>
  applyInlineEditMode(
    props.columns as ColumnConfig<Row>[],
    prefs.inlineEditMode
  )
);
</script>

<template>
  <el-card>
    <SmartTable
      :data="rows"
      :columns="resolvedUserColumns"
      :loading="loading"
      :has-fetched-once="hasFetchedOnce"
      :inline-edit-loading="inlineEditLoading"
      @save="(row: Row, field: RowField) => { const f = asEditable(field); if (f) emit('save', row, f); }"
      @cancel="(row: Row) => emit('cancel', row)"
      @auto-save="(row: Row, field: RowField) => { const f = asEditable(field); if (f) emit('auto-save', row, f); }"
    >
      <template #revertSlots="{ row, field }">
        <el-tooltip
          :content="(() => {
            const f = asEditable(field as RowField);
            return f ? `Previous: ${props.getPreviousValue(row, f)}` : '—';
          })()"
          placement="top"
        >
          <el-icon
            class="cursor-pointer"
            @click="(() => {
              const f = asEditable(field as RowField);
              if (f) emit('revert-field', row, f);
            })()"
          >
            <Refresh />
          </el-icon>
        </el-tooltip>
      </template>

      <template #status="{ row }">
        <InlineStatusCell
          :row-id="row.id"
          :value="row.status ?? Status.ACTIVE"
          :editing-row-id="props.editingStatusRowId"
          :draft="props.statusDraft"
          :options="statusOptions"
          :tag-type="props.statusTagType"
          :format-label="props.formatStatusLabel"
          :disabled="props.inlineEditLoading?.[row.id] ?? false"
          :loading="props.statusSaving?.[String(row.id)] ?? false"
          @start="emit('start-edit-status', row)"
          @cancel="emit('cancel-edit-status')"
          @save="(val) => emit('save-status', row, val)"
          @update:draft="(val) => emit('update-status-draft', val)"
        />
      </template>

      <template #operation="{ row }">
        <ActionButtons :row="row" :rowId="row.id" :role="row.role" />
      </template>
    </SmartTable>
  </el-card>
</template>
