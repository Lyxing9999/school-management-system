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

import { useAuthStore } from "~/stores/authStore";
import { iamService } from "~/api/iam";

type ThemeKey = "light" | "dark";

const emit = defineEmits<{
  (e: "toggle-sidebar"): void;
}>();

const authStore = useAuthStore();
const iam = iamService();

const unreadNotifications = ref(5);
const theme = ref<ThemeKey>("light");
const isDark = computed(() => theme.value === "dark");

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

function getInitialTheme(): ThemeKey {
  if (process.server) return "light";
  const saved = localStorage.getItem("theme") as ThemeKey | null;
  if (saved === "light" || saved === "dark") return saved;

  const attr = document.documentElement.getAttribute(
    "data-theme"
  ) as ThemeKey | null;
  if (attr === "light" || attr === "dark") return attr;

  return "light";
}

onMounted(() => {
  applyTheme(getInitialTheme());
});

const handleNotificationClick = () => {};
const handleProfileClick = async () => navigateTo("/profile");
const handleLogoutClick = async () => iam.auth.logout();
</script>

<template>
  <div class="header-inner">
    <!-- Left: mobile toggle ONLY -->
    <div class="header-left">
      <el-button
        type="text"
        class="icon-button mobile-toggle"
        aria-label="Toggle sidebar"
        @click="emit('toggle-sidebar')"
      >
        <el-icon><Menu /></el-icon>
      </el-button>
    </div>

    <div class="header-center" />

    <div class="header-right">
      <el-space size="small" alignment="center">
        <el-tooltip content="Notifications" placement="bottom">
          <el-badge
            :value="unreadNotifications"
            :hidden="unreadNotifications === 0"
            class="notification-badge"
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

        <el-tooltip
          :content="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          placement="bottom"
        >
          <el-button type="text" class="icon-button" @click="toggleDark">
            <el-icon v-if="isDark"><Sunny /></el-icon>
            <el-icon v-else><Moon /></el-icon>
          </el-button>
        </el-tooltip>

        <el-dropdown trigger="click" placement="bottom-end">
          <el-button type="text" class="user-dropdown">
            <el-space size="small" alignment="center">
              <el-avatar :size="28">
                <UserIcon />
              </el-avatar>

              <span class="user-name">{{ displayName }}</span>
              <el-icon class="chev"><ArrowDown /></el-icon>
            </el-space>
          </el-button>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleProfileClick"
                >Profile</el-dropdown-item
              >
              <el-dropdown-item divided @click="handleLogoutClick"
                >Logout</el-dropdown-item
              >
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-space>
    </div>
  </div>
</template>

<style scoped>
.header-inner {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;

  padding: 0 12px;
  background: var(--header-bg);
  color: var(--text-color);
}

.header-left,
.header-center,
.header-right {
  min-width: 0;
  display: flex;
  align-items: center;
}

.header-center {
  flex: 1 1 auto;
}

.icon-button {
  border-radius: 10px;
  color: var(--muted-color);
  transition: background-color var(--transition-base),
    color var(--transition-base);
}

.icon-button:hover {
  background: var(--hover-bg);
  color: var(--text-color);
}

/* Only show sidebar toggle on mobile */
.mobile-toggle {
  display: none;
}

@media (max-width: 768px) {
  .mobile-toggle {
    display: inline-flex;
  }
}

/* Hide username on small screens */
@media (max-width: 640px) {
  .user-name {
    display: none;
  }
}
</style>
