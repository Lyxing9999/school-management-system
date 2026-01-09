<script setup lang="ts">
const props = defineProps<{
  title: string;
  description?: string;
  rightText?: string;
  padding?: string;
}>();

const bodyStyle = computed(() => ({
  padding: props.padding ?? "20px",
}));
</script>

<template>
  <el-card shadow="never" :body-style="bodyStyle" class="table-card">
    <template #header>
      <div class="table-card__header">
        <div class="table-card__left">
          <div class="table-card__title">{{ title }}</div>
          <p v-if="description" class="table-card__desc">{{ description }}</p>
        </div>

        <div class="table-card__right">
          <span v-if="rightText">{{ rightText }}</span>
          <slot name="header-right" />
        </div>
      </div>
    </template>

    <slot />
  </el-card>
</template>

<style scoped>
.table-card {
  border-radius: 16px; /* matches rounded-2xl */
  border: 1px solid color-mix(in srgb, var(--border-color) 60%, transparent);
  background: var(--color-card);
  box-shadow: 0 1px 2px color-mix(in srgb, var(--card-shadow) 65%, transparent);
}

.table-card__header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (min-width: 640px) {
  .table-card__header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.table-card__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

.table-card__desc {
  font-size: 0.75rem;
  color: var(--muted-color);
  margin-top: 0.25rem;
}

.table-card__right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--muted-color);
}
</style>
