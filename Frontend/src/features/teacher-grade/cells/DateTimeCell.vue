<script setup lang="ts">
import { computed } from "vue";

type DateLike = string | number | Date | null | undefined;

const props = defineProps<{
  value?: DateLike;
}>();

function toDate(value: DateLike): Date | null {
  if (value == null || value === "") return null;
  const d = value instanceof Date ? value : new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
}

const text = computed(() => {
  const d = toDate(props.value);
  if (!d) return props.value ? String(props.value) : "-";

  // Local time, stable output: YYYY-MM-DD HH:mm (24h)
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  const hh = String(d.getHours()).padStart(2, "0");
  const mi = String(d.getMinutes()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`;
});
</script>

<template>
  <span>{{ text }}</span>
</template>
