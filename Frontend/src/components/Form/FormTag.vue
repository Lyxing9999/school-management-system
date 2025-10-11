<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue";
import { ElInput, ElTag } from "element-plus";

const props = defineProps<{
  modelValue: string[];
  placeholder?: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string[]): void;
}>();

const inputVal = ref("");
const tags = ref<string[]>([...(props.modelValue || [])]);

// Sync external modelValue changes
watch(
  () => props.modelValue,
  (val) => {
    tags.value = val || [];
  }
);

// Add tag
const addTag = async () => {
  const val = inputVal.value.trim();
  if (val && !tags.value.includes(val)) {
    tags.value.push(val);
    emit("update:modelValue", [...tags.value]);
  }
  inputVal.value = "";
  await nextTick();
};

// Remove tag
const removeTag = (tag: string) => {
  tags.value = tags.value.filter((t) => t !== tag);
  emit("update:modelValue", [...tags.value]);
};
</script>

<template>
  <div
    class="tag-textarea"
    style="
      min-height: 80px;
      padding: 4px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      align-items: center;
      cursor: text;
    "
    @click="$refs.inputRef?.focus()"
  >
    <ElTag
      v-for="tag in tags"
      :key="tag"
      size="small"
      closable
      @close="removeTag(tag)"
    >
      {{ tag }}
    </ElTag>
    <ElInput
      v-model="inputVal"
      ref="inputRef"
      :placeholder="placeholder || 'Type and press Enter'"
      border="none"
      style="flex: 1; min-width: 100px; padding: 0; height: 28px"
      @keyup.enter="addTag"
    />
  </div>
</template>
