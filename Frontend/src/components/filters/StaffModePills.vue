<script setup lang="ts">
export type StaffMode = "default" | "user" | "staff";

const props = defineProps<{
  modelValue: StaffMode;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", v: StaffMode): void;
}>();

function setMode(v: StaffMode) {
  if (props.disabled) return;
  if (props.modelValue === v) return;
  emit("update:modelValue", v);
}
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <el-check-tag
      :checked="props.modelValue === 'default'"
      size="small"
      @change="(checked: boolean) => checked && setMode('default')"
    >
      Default
    </el-check-tag>

    <el-check-tag
      :checked="props.modelValue === 'user'"
      size="small"
      @change="(checked: boolean) => checked && setMode('user')"
    >
      User
    </el-check-tag>

    <el-check-tag
      :checked="props.modelValue === 'staff'"
      size="small"
      @change="(checked: boolean) => checked && setMode('staff')"
    >
      Staff
    </el-check-tag>
  </div>
</template>
