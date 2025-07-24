<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
import { onMounted } from "vue";

onMounted(() => {
  const savedTheme = localStorage.getItem("dark");
  if (savedTheme === "true") {
    document.documentElement.classList.add("dark");
  }
});
</script>
