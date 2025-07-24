<script setup lang="ts">
defineProps<{
  model: Record<string, any>;
  rules?: any;
  loading?: boolean;
}>();

const emit = defineEmits(["submit"]);
const onSubmit = () => emit("submit");


</script>
<template>
  <el-form
    :model="model"
    :rules="rules"
    label-position="top"
    @submit.prevent="onSubmit"
    class="space-y-4"
  >
    <slot />
    <el-form-item>
      <slot name="actions">
        <el-button type="primary" native-type="submit" :loading="loading">
          Submit
        </el-button>
      </slot>
    </el-form-item>
  </el-form>
</template>
