<script
  setup
  lang="ts"
  generic="R extends Record<string, any>, F extends keyof R = keyof R"
>
import { inject, computed, unref } from "vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import { ElTooltip } from "element-plus";
import { Delete, View } from "@element-plus/icons-vue";

const props = defineProps<{
  rowId: number | string;
  row: R;
  role?: string;
  size?: "small" | "default" | "large" | string;
}>();

const actions = inject<any>("USER_ACTIONS", {
  onDelete: (row: R) => {},
  onOpenEdit: (row: R) => {},
});

const state = inject<any>("USER_STATE", {
  deleteLoading: { value: {} },
  inlineEditLoading: { value: {} },
  isDetailLoading: (id: any) => false,
});

const isDeleteLoading = computed(
  () => unref(state.deleteLoading)?.[props.rowId] ?? false
);

const isDetailLoading = computed(() => {
  const formLoading = state.isDetailLoading
    ? state.isDetailLoading(props.rowId)
    : false;

  const inlineLoading = unref(state.inlineEditLoading)?.[props.rowId] ?? false;
  return formLoading || inlineLoading;
});

const handleDelete = () => {
  if (actions.onDelete) {
    actions.onDelete(props.row || { id: props.rowId });
  }
};

const handleDetail = () => {
  if (actions.onOpenEdit) {
    actions.onOpenEdit(props.row || { id: props.rowId });
  }
};

defineSlots<{
  extra?: (slotProps: { rowId: number | string; row: R }) => any;
}>();
</script>

<template>
  <div class="flex items-center gap-2 justify-center">
    <ElTooltip content="Edit Details" placement="top">
      <BaseButton
        type="text"
        class="button-detail"
        :size="size || 'default'"
        :loading="isDetailLoading"
        :disabled="isDetailLoading || isDeleteLoading"
        @click="handleDetail"
      >
        <template #iconPre
          ><el-icon class="mr-2"><View /></el-icon
        ></template>
        Detail
      </BaseButton>
    </ElTooltip>

    <ElTooltip content="Delete User" placement="top">
      <BaseButton
        type="text"
        class="button-delete"
        :size="size || 'default'"
        :loading="isDeleteLoading"
        :disabled="isDeleteLoading || isDetailLoading"
        @click="handleDelete"
      >
        <template #iconPre
          ><el-icon class="mr-2"><Delete /></el-icon
        ></template>
        Delete
      </BaseButton>
    </ElTooltip>

    <slot name="extra" :row-id="rowId" :row="row" />
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
