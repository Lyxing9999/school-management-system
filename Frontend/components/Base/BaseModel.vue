<script setup lang="ts">
import type { FormInstance } from "element-plus";

const props = defineProps<{
  model: any;
  rules: any;
  fields: any;
}>();

const formRef = ref<FormInstance>();

const emit = defineEmits<{
  (e: "submit", value: any): void;
}>();

const handleSubmit = () => {
  formRef.value?.validate((valid: boolean) => {
    if (valid) {
      emit("submit", props.model);
    }
  });
};
</script>

<template>
  <el-form
    :model="model"
    :rules="rules"
    ref="formRef"
    @submit.prevent="handleSubmit"
  >
    <el-form-item
      v-for="field in fields"
      :key="field.name"
      :label="field.label"
      :prop="field.name"
    >
      <component :is="field.component" v-model="model[field.name]" />
    </el-form-item>
    <el-button type="primary" @click="handleSubmit">Submit</el-button>
  </el-form>
</template>

<style scoped></style>
