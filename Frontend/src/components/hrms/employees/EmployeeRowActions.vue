<script setup lang="ts">
import { computed } from "vue";
import { Delete, EditPen, RefreshLeft, View } from "@element-plus/icons-vue";
import BaseButton from "~/components/base/BaseButton.vue";

interface EmployeeTableRow {
  id: string;
  full_name: string;
  deleted_at: string | null;
}

const props = defineProps<{
  row: EmployeeTableRow;
  loading?: boolean;
}>();

const emit = defineEmits<{
  (e: "detail", row: EmployeeTableRow): void;
  (e: "assign-schedule", row: EmployeeTableRow): void;
  (e: "delete", row: EmployeeTableRow): void;
  (e: "restore", row: EmployeeTableRow): void;
}>();

const isDeleted = computed(() => !!props.row.deleted_at);
</script>

<template>
  <div class="row-actions">
    <BaseButton
      type="primary"
      plain
      size="small"
      class="row-actions__button"
      @click="emit('detail', row)"
    >
      <template #iconPre>
        <el-icon><View /></el-icon>
      </template>
      Detail
    </BaseButton>

    <BaseButton
      type="warning"
      plain
      size="small"
      class="row-actions__button"
      @click="emit('assign-schedule', row)"
    >
      <template #iconPre>
        <el-icon><EditPen /></el-icon>
      </template>
      Assign
    </BaseButton>

    <BaseButton
      v-if="!isDeleted"
      type="danger"
      plain
      size="small"
      class="row-actions__button"
      :loading="loading"
      @click="emit('delete', row)"
    >
      <template #iconPre>
        <el-icon><Delete /></el-icon>
      </template>
      Delete
    </BaseButton>

    <BaseButton
      v-else
      type="success"
      plain
      size="small"
      class="row-actions__button"
      :loading="loading"
      @click="emit('restore', row)"
    >
      <template #iconPre>
        <el-icon><RefreshLeft /></el-icon>
      </template>
      Restore
    </BaseButton>
  </div>
</template>

<style scoped>
.row-actions {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: max-content;
  align-items: center;
  gap: 6px;
  min-width: 0;
  padding: 6px 8px;
  border-radius: 12px;
  background: var(--surface-soft, rgba(255, 255, 255, 0.04));
}

.row-actions__button :deep(.el-button),
.row-actions__button :deep(button) {
  min-height: 30px;
  padding-inline: 8px;
}

.row-actions :deep(.el-button) {
  border-radius: 8px;
  font-weight: 600;
}

.row-actions :deep(.el-button.is-plain) {
  transition: background-color var(--transition-base, 0.2s ease),
    color var(--transition-base, 0.2s ease),
    opacity var(--transition-base, 0.2s ease),
    transform var(--transition-base, 0.2s ease);
}

.row-actions :deep(.el-button.is-plain:hover) {
  background: var(--hover-bg, rgba(255, 255, 255, 0.08));
}

.row-actions :deep(.el-button.is-plain:active) {
  transform: translateY(0.3px);
}

.row-actions :deep(.el-button.is-loading) {
  opacity: 0.85;
}

@media (max-width: 720px) {
  .row-actions {
    grid-auto-flow: row;
    padding: 4px 6px;
  }

  .row-actions__button :deep(.el-button) {
    width: 100%;
  }
}
</style>
