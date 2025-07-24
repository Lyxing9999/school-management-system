<script setup lang="ts">
const props = defineProps<{
  modelValue: string | number | null;
  placeholder?: string;
  clearable?: boolean;
  size?: "default" | "small" | "large";
  prefixIcon?: string;
  suffixIcon?: string;
}>();

const model = defineModel<typeof props.modelValue>();

const emit = defineEmits<{
  (e: "search", value: typeof props.modelValue): void;
}>();

function handleEnter() {
  emit("search", model.value as typeof props.modelValue);
}
</script>

<template>
  <el-input
    v-model="model"
    :placeholder="placeholder"
    :clearable="clearable"
    :prefix-icon="prefixIcon"
    :suffix-icon="suffixIcon"
    :size="size"
    @keyup.enter.native="handleEnter"
  >
    <template #suffix>
      <slot
        name="suffix"
        :inputValue="model"
        :updateValue="(v: string | number) => (model = v)"
        :search="handleEnter"
      />
    </template>
  </el-input>
</template>
