<script setup lang="ts">
import { computed } from "vue";
import { ElTag } from "element-plus";
import type { GradeType } from "~/api/types/school.dto";

type TagType = "success" | "warning" | "danger" | "info";

const props = defineProps<{
  type?: GradeType | string | null;
}>();

const TYPE_MAP = {
  exam: { tag: "success", label: "Exam" },
  assignment: { tag: "warning", label: "Assignment" },
  homework: { tag: "info", label: "Homework" },
  quiz: { tag: "warning", label: "Quiz" },
} as const satisfies Record<string, { tag: TagType; label: string }>;

const cfg = computed(() => {
  const raw = props.type == null ? "" : String(props.type);
  const key = raw.trim().toLowerCase();

  if ((Object.keys(TYPE_MAP) as GradeType[]).includes(key as GradeType)) {
    const found = TYPE_MAP[key as GradeType];
    return { type: found.tag, label: found.label };
  }

  if (!key) return { type: "info" as const, label: "N/A" };
  return { type: "info" as const, label: raw };
});
</script>

<template>
  <ElTag :type="cfg.type" effect="plain" size="small">
    {{ cfg.label }}
  </ElTag>
</template>
