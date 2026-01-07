<script setup lang="ts">
import { computed } from "vue";
import { ElTag } from "element-plus";

type TagType = "success" | "warning" | "danger" | "info";

const props = defineProps<{
  score?: number | null;
}>();

const model = computed((): { type: TagType; text: string } => {
  const v = props.score;

  if (v == null) return { type: "info", text: "N/A" };

  const n = Number(v);
  if (Number.isNaN(n)) return { type: "info", text: String(v) };

  if (n >= 90) return { type: "success", text: `${n} / 100` };
  if (n >= 70) return { type: "warning", text: `${n} / 100` };
  return { type: "danger", text: `${n} / 100` };
});
</script>

<template>
  <ElTag :type="model.type" effect="plain" size="small">
    {{ model.text }}
  </ElTag>
</template>
