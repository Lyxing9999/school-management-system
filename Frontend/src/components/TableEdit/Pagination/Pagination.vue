<script setup lang="ts">
import { computed, defineProps, defineEmits } from "vue";
import BaseButton from "~/components/Base/BaseButton.vue";

const props = defineProps({
  currentPage: { type: Number, required: true },
  pageSize: { type: Number, required: true },
  total: { type: Number, required: true },
  className: { type: String, default: "" },
  style: { type: Object as () => Record<string, string>, default: () => ({}) },
});

const emits = defineEmits<{
  (e: "page-change", page: number): void;
}>();

const totalPages = computed(() =>
  Math.max(Math.ceil(props.total / props.pageSize), 1)
);
const canPrev = computed(() => props.currentPage > 1);
const canNext = computed(() => props.currentPage < totalPages.value);

const goPrev = () =>
  canPrev.value && emits("page-change", props.currentPage - 1);
const goNext = () =>
  canNext.value && emits("page-change", props.currentPage + 1);
</script>

<template>
  <div
    class="flex items-center space-x-2 p-2 bg-white rounded shadow-sm"
    :class="className"
    :style="style"
  >
    <BaseButton @click="goPrev" type="primary" :disabled="!canPrev"
      >Prev</BaseButton
    >
    <span class="font-medium text-gray-700"
      >Page {{ currentPage }} of {{ totalPages }}</span
    >
    <BaseButton @click="goNext" type="primary" :disabled="!canNext"
      >Next</BaseButton
    >
  </div>
</template>
