<script setup lang="ts">
import { computed } from "vue";
import { Loading } from "@element-plus/icons-vue";

type StatusValue = string;

type StatusOption<V extends StatusValue = StatusValue> = {
  label: string;
  value: V;
};

const props = withDefaults(
  defineProps<{
    rowId: string | number;
    value?: StatusValue | null;

    editingRowId: string | number | null;
    draft: StatusValue;

    options: StatusOption[];

    tagType: (v?: StatusValue | null) => any;
    formatLabel: (v?: StatusValue | null) => string;

    tooltip?: string;
    size?: "small" | "default" | "large";

    /** Disable interactions (e.g., inlineEditLoading) */
    disabled?: boolean;

    /** Saving/loading (e.g., statusSaving) */
    loading?: boolean;
  }>(),
  {
    tooltip: "Click to change status",
    size: "small",
    disabled: false,
    loading: false,
  }
);

const emit = defineEmits<{
  (e: "start"): void;
  (e: "cancel"): void;
  (e: "save", value: StatusValue): void;
  (e: "update:draft", value: StatusValue): void;
}>();

const isEditing = computed(() => {
  if (props.editingRowId == null) return false;
  return String(props.editingRowId) === String(props.rowId);
});

const isBlocked = computed(() => props.disabled || props.loading);

function start() {
  if (isBlocked.value) return;
  emit("start");
}

function cancel() {
  if (props.loading) return;
  emit("cancel");
}

function save(val: StatusValue) {
  if (props.loading) return;
  emit("save", val);
}
</script>

<template>
  <div class="inline-status">
    <el-tooltip :content="tooltip" placement="top" :show-after="200">
      <div class="status-slot">
        <transition name="fade-scale" mode="out-in">
          <!-- View -->
          <button
            v-if="!isEditing"
            :key="`view-${rowId}`"
            type="button"
            class="status-btn"
            :disabled="isBlocked"
            @click="start"
            @keydown.enter.prevent="start"
          >
            <el-tag
              :type="tagType(value)"
              effect="light"
              round
              class="status-pill"
              :class="{ 'is-disabled': isBlocked }"
            >
              <span class="status-text">{{ formatLabel(value) }}</span>

              <!-- reserve space so width doesn't jump -->
              <span class="status-right" aria-hidden="true">
                <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
              </span>
            </el-tag>
          </button>

          <!-- Edit -->
          <div v-else :key="`edit-${rowId}`" class="status-edit">
            <el-select
              :model-value="draft"
              :size="size"
              class="status-select"
              :disabled="isBlocked"
              :loading="loading"
              @update:model-value="(v) => emit('update:draft', v as any)"
              @change="(v) => save(v as any)"
              @keydown.esc.prevent="cancel"
              @keydown.enter.prevent
              @visible-change="
                (open) => {
                  if (!open) cancel();
                }
              "
            >
              <el-option
                v-for="opt in options"
                :key="String(opt.value)"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>

            <span class="status-right" aria-hidden="true">
              <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
            </span>
          </div>
        </transition>
      </div>
    </el-tooltip>
  </div>
</template>

<style scoped>
/* Table-safe: allow shrinking inside el-table cell */
.inline-status {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-width: 0;
}

.status-slot {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-width: 0;
}

/* Use button wrapper for accessibility + no layout issues */
.status-btn {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-width: 0;
  padding: 0;
  border: 0;
  background: transparent;
}
.status-btn:disabled {
  cursor: not-allowed;
}

/* Tag appearance */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  min-width: 0;
  cursor: pointer;
  user-select: none;
  font-weight: 600;
  border-radius: 999px;
  padding: 4px 10px;
}

.status-pill.is-disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

/* Truncate long labels safely */
.status-text {
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Reserve spinner space so width doesn't jump */
.status-right {
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  width: 14px;
  flex: 0 0 auto;
}

/* Edit layout */
.status-edit {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  min-width: 0;
}

/* Let select fit the column */
.status-select {
  max-width: 100%;
  width: auto;
  min-width: 0;
}

/* Element Plus shrink fixes */
:deep(.el-select) {
  max-width: 100%;
  min-width: 0;
}
:deep(.el-select .el-input) {
  max-width: 100%;
  min-width: 0;
}
:deep(.el-select .el-input__wrapper) {
  max-width: 100%;
}

/* Motion */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.12s ease;
}
.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.98);
}
</style>
