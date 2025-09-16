<script setup lang="ts">
const props = defineProps<{
  loading?: boolean;
  disabled?: boolean;
  title?: string;
  confirmText?: string;
  cancelText?: string;
}>();

const emit = defineEmits<{
  (e: "confirm"): void;
  (e: "cancel"): void;
}>();

function onConfirm() {
  emit("confirm");
}

function onCancel() {
  emit("cancel");
}
</script>

<template>
  <div class="flex items-center space-x-1">
    <el-popconfirm
      :title="title || 'Are you sure you want to save the changes?'"
      :confirm-button-text="confirmText || 'Yes'"
      :cancel-button-text="cancelText || 'No'"
      @confirm="onConfirm"
      @cancel="onCancel"
    >
      <template #reference>
        <el-button
          class="compact-btn"
          type="text"
          size="small"
          :loading="props.loading"
          aria-label="Save"
        >
          <el-icon><Edit /></el-icon>
        </el-button>
      </template>
    </el-popconfirm>

    <el-button
      class="compact-btn"
      type="text"
      size="small"
      aria-label="Cancel"
      @click="onCancel"
      :disabled="props.loading"
    >
      <el-icon><Close /></el-icon>
    </el-button>
  </div>
</template>

<style scoped>
.compact-btn {
  padding: 2px 6px;
}
</style>
