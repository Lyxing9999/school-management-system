<script
  setup
  lang="ts"
  generic="R extends Record<string, any>, F extends keyof R = keyof R"
>
import { inject, computed, unref } from "vue";
import type { Ref } from "vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { ElTooltip } from "element-plus";
import { Delete, View, Key } from "@element-plus/icons-vue";

const props = defineProps<{
  rowId: number | string;
  row: R;
  role?: string;
  size?: "small" | "default" | "large" | string;
}>();

type UserActions<R> = {
  onDelete?: (row: R) => void | Promise<void>;
  onOpenEdit?: (row: R) => void | Promise<void>;
  onResetPassword?: (row: R) => void | Promise<void>;
};

const actions = inject<UserActions<R>>("USER_ACTIONS", {
  onDelete: (_row: R) => {},
  onOpenEdit: (_row: R) => {},
  onResetPassword: (_row: R) => {},
});

type LoadingMap = Record<string, boolean>;

type UserState = {
  deleteLoading?: Ref<LoadingMap> | LoadingMap;
  inlineEditLoading?: Ref<LoadingMap> | LoadingMap;
  resetPasswordLoading?: Ref<LoadingMap> | LoadingMap;
  isDetailLoading?: (id: number | string) => boolean;
};

const state = inject<UserState>("USER_STATE", {
  deleteLoading: { value: {} } as any,
  inlineEditLoading: { value: {} } as any,
  resetPasswordLoading: { value: {} } as any,
  isDetailLoading: (_id: any) => false,
});

const rowKey = computed(() => String(props.rowId));

const isDeleteLoading = computed(() => {
  const map = unref(state.deleteLoading) as LoadingMap | undefined;
  return map?.[rowKey.value] ?? false;
});

const isResetLoading = computed(() => {
  const map = unref(state.resetPasswordLoading) as LoadingMap | undefined;
  return map?.[rowKey.value] ?? false;
});

const isDetailLoading = computed(() => {
  const formLoading = state.isDetailLoading
    ? state.isDetailLoading(props.rowId)
    : false;

  const inlineMap = unref(state.inlineEditLoading) as LoadingMap | undefined;
  const inlineLoading = inlineMap?.[rowKey.value] ?? false;

  return formLoading || inlineLoading;
});

const isAnyBusy = computed(
  () => isDetailLoading.value || isDeleteLoading.value || isResetLoading.value
);
const handleDelete = async () => {
  await actions?.onDelete?.(props.row);
};

const handleDetail = async () => {
  await actions?.onOpenEdit?.(props.row);
};

const handleResetPassword = async () => {
  await actions?.onResetPassword?.(props.row);
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
        :size="size || 'small'"
        :loading="isDetailLoading"
        :disabled="isAnyBusy"
        @click="handleDetail"
      >
        <template #iconPre>
          <el-icon class="mr-2"><View /></el-icon>
        </template>
        Detail
      </BaseButton>
    </ElTooltip>

    <ElTooltip content="Reset Password" placement="top">
      <BaseButton
        type="text"
        class="button-reset"
        :size="size || 'small'"
        :loading="isResetLoading"
        :disabled="isAnyBusy"
        @click="handleResetPassword"
      >
        <template #iconPre>
          <el-icon class="mr-2"><Key /></el-icon>
        </template>
        Reset
      </BaseButton>
    </ElTooltip>

    <ElTooltip content="Delete User" placement="top">
      <BaseButton
        type="text"
        class="button-delete"
        :size="size || 'small'"
        :loading="isDeleteLoading"
        :disabled="isAnyBusy"
        @click="handleDelete"
      >
        <template #iconPre>
          <el-icon class="mr-2"><Delete /></el-icon>
        </template>
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

/* Reset Password */
.button-reset {
  border-radius: 10px;
  font-size: 13px;
  font-weight: 650;
  border: 1px solid color-mix(in srgb, var(--el-color-warning) 25%, transparent);
  color: var(--el-color-warning);
  background: transparent;
  transition: transform var(--transition-base),
    background-color var(--transition-base), border-color var(--transition-base),
    color var(--transition-base);
}

.button-reset:hover {
  background-color: color-mix(
    in srgb,
    var(--el-color-warning) 12%,
    transparent
  );
  border-color: color-mix(in srgb, var(--el-color-warning) 40%, transparent);
  transform: translateY(-0.5px);
}
.button-reset:active {
  transform: translateY(0);
  background-color: color-mix(
    in srgb,
    var(--el-color-warning) 18%,
    transparent
  );
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
