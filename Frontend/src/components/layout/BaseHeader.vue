<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { navigateTo } from "nuxt/app";
import {
  Menu,
  Bell,
  Sunny,
  Moon,
  ArrowDown,
  User as UserIcon,
} from "@element-plus/icons-vue";

import BaseInputSearch from "~/components/Base/BaseInputSearch.vue";
import { useAuthStore } from "~/stores/authStore";
import { iamService } from "~/api/iam"; // adjust path to where your iamService() file is
// Example: "~/api/iam/index" or "~/services/iam" depending on your project
// Use the real path you created.

type ThemeKey = "light" | "dark";

const emit = defineEmits<{
  (e: "toggle-sidebar"): void;
}>();

const authStore = useAuthStore();
const iam = iamService();

const searchQuery = ref("");
const unreadNotifications = ref(5);

const theme = ref<ThemeKey>("light");
const isDark = computed(() => theme.value === "dark");

// Since your store is Composition API (refs), prefer .value in script
const displayName = computed(() => {
  if (!authStore.isReady) return "Loading...";
  return authStore.user?.username ?? "Admin User";
});

function applyTheme(next: ThemeKey) {
  theme.value = next;

  const el = document.documentElement;
  el.setAttribute("data-theme", next);
  el.classList.toggle("dark", next === "dark");

  localStorage.setItem("theme", next);
}

function toggleDark() {
  applyTheme(isDark.value ? "light" : "dark");
}

onMounted(() => {
  const current =
    (document.documentElement.getAttribute("data-theme") as ThemeKey) ??
    "light";
  theme.value = current;
});

const handleNotificationClick = () => {
  console.log("Notification clicked");
};

const handleProfileClick = async () => {
  await navigateTo("/profile"); 
};

const handleLogoutClick = async () => {
  await iam.auth.logout();
};
</script>

<template>
  <div class="header-inner">
    <!-- Left -->
    <div class="header-left">
      <el-button
        type="text"
        class="icon-button mobile-toggle"
        @click="emit('toggle-sidebar')"
      >
        <el-icon><Menu /></el-icon>
      </el-button>
    </div>

    <!-- Center -->
    <div class="header-center">
      <!-- Center header -->
      <!-- <BaseInputSearch v-model="searchQuery" /> -->
    </div>

    <!-- Right -->
    <div class="header-right">
      <el-space size="small" alignment="center">
        <el-tooltip content="Notifications" placement="bottom">
          <el-badge
            :value="unreadNotifications"
            class="notification-badge"
            :hidden="unreadNotifications === 0"
          >
            <el-button
              type="text"
              class="icon-button"
              @click="handleNotificationClick"
            >
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
        </el-tooltip>

        <!-- Theme toggle -->
        <el-tooltip
          :content="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          placement="bottom"
        >
          <el-button @click="toggleDark" type="text" class="icon-button">
            <el-icon v-if="isDark"><Sunny /></el-icon>
            <el-icon v-else><Moon /></el-icon>
          </el-button>
        </el-tooltip>

        <!-- User dropdown -->
        <el-dropdown trigger="click" placement="bottom-end">
          <el-button type="text" class="user-dropdown">
            <el-space size="small" alignment="center">
              <el-avatar :size="28">
                <UserIcon />
              </el-avatar>
              <span class="user-name">{{ displayName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </el-space>
          </el-button>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleProfileClick">
                Profile
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogoutClick">
                Logout
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-space>
    </div>
  </div>
</template>
