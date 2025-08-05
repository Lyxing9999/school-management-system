<script setup lang="ts">
import { ref, watch, computed, provide } from "vue";
import {
  Menu,
  Bell,
  Sunny,
  Moon,
  ArrowDown,
  User,
} from "@element-plus/icons-vue";
import { useDarkMode } from "~/composables/useDarkMode";
import BaseInputSearch from "~/components/Base/BaseInputSearch.vue";
import { debounce } from "lodash-es";

const searchQuery = ref("");
provide("searchQuery", searchQuery);

const emit = defineEmits<{
  (e: "toggle-sidebar"): void;
  (e: "search", q: string): void;
  (e: "notification-click"): void;
  (e: "profile-click"): void;
  (e: "logout-click"): void;
}>();

watch(
  searchQuery,
  debounce((val: string) => {
    emit("search", val);
  }, 300)
);

const props = withDefaults(
  defineProps<{
    searchPlaceholder?: string;
    searchClearable?: boolean;
    searchSize?: "default" | "small" | "large";

    mobileToggleClass?: string;
    searchClass?: string;
    darkModeToggleClass?: string;
    userDropdownClass?: string;
    userDropdownItemClass?: string;

    userName?: string;
    avatarIcon?: string;
    notificationCount?: number;
  }>(),
  {
    searchPlaceholder: "Search...",
    searchClearable: true,
    searchSize: "default",

    mobileToggleClass: "",
    searchClass: "",
    darkModeToggleClass: "",
    userDropdownClass: "",
    userDropdownItemClass: "",

    userName: "Admin User",
    avatarIcon: "User",
    notificationCount: 0,
  }
);

const { isDark, toggleDark } = useDarkMode();
</script>

<template>
  <el-header>
    <el-row justify="space-between" align="middle" style="height: 100%">
      <el-col :span="6">
        <el-space>
          <el-button
            :class="props.mobileToggleClass"
            @click="$emit('toggle-sidebar')"
            type="text"
            class="mobile-toggle"
            aria-label="Toggle sidebar"
          >
            <el-icon><Menu /></el-icon>
          </el-button>
        </el-space>
      </el-col>

      <el-col :span="12">
        <BaseInputSearch
          v-model="searchQuery"
          :class="props.searchClass"
          :placeholder="props.searchPlaceholder"
          :clearable="props.searchClearable"
          :size="props.searchSize"
          class="search-input"
        />
      </el-col>

      <el-col :span="6">
        <el-space>
          <el-tooltip content="Notifications" placement="bottom">
            <el-badge
              :value="props.notificationCount"
              class="notification-badge"
              @click="$emit('notification-click')"
            >
              <el-button
                type="text"
                class="icon-button"
                aria-label="Notifications"
              >
                <el-icon><Bell /></el-icon>
              </el-button>
            </el-badge>
          </el-tooltip>

          <el-tooltip
            :content="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
            placement="bottom"
            :class="props.darkModeToggleClass"
          >
            <el-button
              @click="toggleDark"
              type="text"
              class="icon-button"
              aria-label="Toggle dark mode"
            >
              <el-icon v-if="isDark"><Sunny /></el-icon>
              <el-icon v-else><Moon /></el-icon>
            </el-button>
          </el-tooltip>

          <el-dropdown trigger="click" placement="bottom-end">
            <el-button
              type="text"
              :class="props.userDropdownClass"
              aria-label="User menu"
            >
              <el-space>
                <el-avatar :size="32" :icon="props.avatarIcon" />
                <span class="user-name">{{ props.userName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </el-space>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <slot name="user-dropdown">
                  <el-dropdown-item
                    @click="$emit('profile-click')"
                    :class="props.userDropdownItemClass"
                  >
                    Profile
                  </el-dropdown-item>
                  <el-dropdown-item
                    divided
                    @click="$emit('logout-click')"
                    :class="props.userDropdownItemClass"
                  >
                    Logout
                  </el-dropdown-item>
                </slot>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-space>
      </el-col>
    </el-row>
  </el-header>
</template>

<style scoped lang="scss"></style>
