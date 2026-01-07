<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { eventBus } from "~/composables/system/useGlobalEventBus";
useHead({
  meta: [
    {
      name: "viewport",
      content: "width=device-width, initial-scale=1, viewport-fit=cover",
    },
  ],
});
const handleErrorMessage = (msg: string) => {
  ElMessage.error(msg);
};

const handleSessionExpired = () => {
  ElMessageBox.alert(
    "Your session has expired. Please login again.",
    "Session Expired",
    {
      type: "warning",
      callback: () => {
        window.location.href = "/auth/login";
      },
    }
  );
};

onMounted(() => {
  // Theme Mode
  const savedTheme = localStorage.getItem("dark");
  if (savedTheme === "true") {
    document.documentElement.classList.add("dark");
  }

  // Register EventBus Handlers
  eventBus.on("error-message", handleErrorMessage);
  eventBus.on("session-expired", handleSessionExpired);
});

onBeforeUnmount(() => {
  eventBus.off("error-message", handleErrorMessage);
  eventBus.off("session-expired", handleSessionExpired);
});
</script>
