<script setup lang="ts">
import BaseButton from "~/components/Base/BaseButton.vue";
import { ElTooltip } from "element-plus";
import { Delete, View } from "@element-plus/icons-vue";

defineProps<{
  rowId: number | string;
  loading?: boolean;
  role?: string; // current row role
  onDetail?: (id: number | string) => void;
  onDelete?: (id: number | string) => void;
  hideDetailForRoles?: string[]; // roles to hide Detail button
  detailContent?: string;
  deleteContent?: string;
  attributes?: Record<string, unknown>;
}>();
</script>

<template>
  <div class="flex items-center gap-2 justify-center">
    <ElTooltip
      v-if="
        onDetail &&
        (!hideDetailForRoles || !role || !hideDetailForRoles.includes(role))
      "
      :content="detailContent"
      placement="top"
    >
      <BaseButton
        type="text"
        class="button-detail"
        size="default"
        :loading="loading"
        v-bind="attributes"
        :disabled="loading"
        @click="onDetail?.(rowId)"
        aria-label="View Details"
      >
        <template #iconPre>
          <el-icon class="mr-2"><View /></el-icon>
        </template>
        Detail
      </BaseButton>
    </ElTooltip>

    <ElTooltip v-if="onDelete" :content="deleteContent" placement="top">
      <BaseButton
        type="text"
        class="button-delete"
        size="default"
        :loading="loading"
        :disabled="loading"
        v-bind="attributes"
        @click="onDelete?.(rowId)"
        aria-label="Delete User"
      >
        <template #iconPre>
          <el-icon class="mr-2"><Delete /></el-icon>
        </template>
        Delete
      </BaseButton>
    </ElTooltip>
  </div>
</template>

<style scoped>
.button-detail {
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  border: 1px solid var(--color-primary-light-6);
  transition: transform 0.2s ease;
}
.button-detail:hover {
  transform: translateY(-0.8px);
}
.button-detail:active {
  transform: translateY(0);
}

.button-delete {
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: var(--el-color-danger);
  border-color: var(--el-color-danger-light-7);
  transition: transform 0.2s ease;
}
.button-delete:hover {
  color: var(--el-color-danger);
  background-color: var(--el-color-danger-light-9);
  transform: translateY(-0.5px);
}
.button-delete:active {
  transform: translateY(0);
}
</style>
