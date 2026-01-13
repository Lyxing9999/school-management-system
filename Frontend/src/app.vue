<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { eventBus } from "~/composables/system/useGlobalEventBus";
import { useTheme } from "~/composables/system/useTheme";

const { initSystemPreference } = useTheme();
onMounted(() => {
  // Check system preference only once on mount
  initSystemPreference();
});
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
  eventBus.on("error-message", handleErrorMessage);
  eventBus.on("session-expired", handleSessionExpired);
});

onBeforeUnmount(() => {
  eventBus.off("error-message", handleErrorMessage);
  eventBus.off("session-expired", handleSessionExpired);
});
</script>
