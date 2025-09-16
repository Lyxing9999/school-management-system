<script setup lang="ts">
import BaseButton from "~/components/Base/BaseButton.vue";

defineProps<{
  rowId: number | string;
  loading?: boolean;
  onDetail?: (id: number | string) => void;
  onDelete?: (id: number | string) => void;
}>();
</script>

<template>
  <div class="flex justify-center items-center">
    <BaseButton
      v-if="onDetail"
      type="text"
      class="button-detail"
      size="default"
      :loading="loading"
      @click="() => onDetail?.(rowId)"
    >
      <template v-if="!loading" #iconPre>
        <el-icon class="mr-2"><View /></el-icon>
      </template>
      Detail
    </BaseButton>
    <BaseButton
      v-if="onDelete"
      type="text"
      class="button-delete"
      size="default"
      :loading="loading"
      @click="() => onDelete?.(rowId)"
    >
      <template v-if="!loading" #iconPre>
        <el-icon class="mr-2"><Delete /></el-icon>
      </template>
      Delete
    </BaseButton>
  </div>
</template>
<style scoped>
.button-detail {
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  border: 1px solid var(--color-primary-light-6);
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
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: var(--el-color-danger);
  border-color: var(--el-color-danger-light-7);
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
