<script setup lang="ts">
import { useAuthStore } from "~/stores/authStore";
import BaseHeader from "~/components/layout/BaseHeader.vue";

const headerStyle = { backgroundColor: "#fff" };

const leftSectionClass = "flex items-center gap-4";
const toggleButtonClass = "p-2 text-[var(--color-primary)]";
const searchInputClass =
  "rounded px-3 py-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[var(--color-sidebar-dark)] text-sm";
const rightSectionClass = "flex items-center gap-4";
const notificationBadgeClass =
  "bg-[var(--color-primary)] text-white text-xs rounded-full px-2 py-0.5";
const darkModeButtonClass = "p-2 text-gray-500 dark:text-gray-300";
const userDropdownTriggerClass = "flex items-center gap-2 cursor-pointer";
const userNameClass =
  "text-[var(--color-secondary-dark)] dark:text-[var(--color-secondary-light)] font-semibold text-sm";

const authStore = useAuthStore();
const user = authStore.user;
</script>
<template>
  <div class="w-full">
    <BaseHeader
      :user-name="user?.username"
      :header-style="headerStyle"
      :left-section-class="leftSectionClass"
      :toggle-button-class="toggleButtonClass"
      :search-input-class="searchInputClass"
      :right-section-class="rightSectionClass"
      :notification-badge-class="notificationBadgeClass"
      :dark-mode-button-class="darkModeButtonClass"
      :user-dropdown-trigger-class="userDropdownTriggerClass"
      :user-name-class="userNameClass"
    />
  </div>
</template>
