<script setup lang="ts">
import BaseButton from "~/components/base/BaseButton.vue";
import { ElTooltip } from "element-plus";
import { Delete, View } from "@element-plus/icons-vue";

const props = defineProps<{
  rowId: number | string;
  loading?: boolean;
  role?: string; // current row role
  onDetail?: (id: number | string) => void;
  onDelete?: (id: number | string) => void;
  hideDetailForRoles?: string[]; // roles to hide Detail button
  detailContent?: string;
  deleteContent?: string;
  attributes?: Record<string, unknown>;
  detailLoading: boolean;
  deleteLoading: boolean;
  size?: "small" | "default" | "large" | string;
  detailText?: string;
  deleteText?: string;
}>();

// Optional type for slots
defineSlots<{
  extra?: (slotProps: { rowId: number | string }) => any;
}>();
</script>

<template>
  <div class="flex items-center gap-2 justify-center">
    <!-- DETAIL -->
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
        :size="size || 'small'"
        :loading="detailLoading"
        v-bind="attributes"
        :disabled="detailLoading || deleteLoading"
        @click="onDetail?.(rowId)"
        aria-label="View Details"
        aria-describedby="detail-tooltip"
      >
        <template #iconPre>
          <el-icon class="mr-2"><View /></el-icon>
        </template>
        {{ detailText || "Detail" }}
      </BaseButton>
    </ElTooltip>

    <!-- DELETE -->
    <ElTooltip v-if="onDelete" :content="deleteContent" placement="top">
      <BaseButton
        type="text"
        class="button-delete"
        :size="size || 'small'"
        :loading="deleteLoading"
        :disabled="deleteLoading || detailLoading"
        v-bind="attributes"
        @click="onDelete?.(rowId)"
        aria-label="Delete User"
        aria-describedby="delete-tooltip"
      >
        <template #iconPre>
          <el-icon class="mr-2"><Delete /></el-icon>
        </template>
        {{ deleteText || "Delete" }}
      </BaseButton>
    </ElTooltip>

    <!-- EXTRA SLOT (for Assign / Unassign / anything) -->
    <slot name="extra" :row-id="rowId" />
  </div>
</template>

<style scoped>
.button-detail {
  border-radius: 10px;
  font-size: 13px;
  font-weight: 650;
  border: 1px solid var(--color-primary-light-6);
  color: var(--color-primary);
  background: transparent;
  transition: transform var(--transition-base),
    background-color var(--transition-base), border-color var(--transition-base),
    color var(--transition-base);
}

.button-detail:hover {
  background-color: var(--color-primary-light-9);
  border-color: var(--color-primary-light-4);
  transform: translateY(-0.8px);
}
.button-detail:active {
  transform: translateY(0);
  background-color: var(--color-primary-light-8);
}

.button-delete {
  border-radius: 10px;
  font-size: 13px;
  font-weight: 650;
  border: 1px solid color-mix(in srgb, var(--el-color-danger) 25%, transparent);
  color: var(--el-color-danger);
  background: transparent;
  transition: transform var(--transition-base),
    background-color var(--transition-base), border-color var(--transition-base),
    color var(--transition-base);
}

.button-delete:hover {
  background-color: color-mix(in srgb, var(--el-color-danger) 12%, transparent);
  border-color: color-mix(in srgb, var(--el-color-danger) 40%, transparent);
  transform: translateY(-0.5px);
}
.button-delete:active {
  transform: translateY(0);
  background-color: color-mix(in srgb, var(--el-color-danger) 18%, transparent);
}
</style>
