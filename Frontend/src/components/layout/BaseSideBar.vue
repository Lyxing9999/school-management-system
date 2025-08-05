<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "~/stores/authStore";
import { menus } from "~/constants/menus";

import {
  HomeFilled,
  User,
  Notebook,
  Bell,
  Calendar,
  Setting,
} from "@element-plus/icons-vue";

const props = withDefaults(
  defineProps<{
    isMobile: boolean;
    isCollapsed?: boolean;
    logoSrc: string;
    logoSectionClass?: string;
    menuClass?: string;
    menuItemClass?: string;
    menuIconClass?: string;
    menuTitleClass?: string;
    asideClass?: string;
  }>(),
  {
    isCollapsed: false,
    logoSectionClass: "p-4 flex justify-center items-center mb-4 w-2/3 mx-auto",
    menuClass: "",
    menuItemClass: "",
    menuIconClass: "",
    menuTitleClass: "",
    asideClass: "",
  }
);

const {
  logoSrc,
  logoSectionClass,
  menuClass,
  menuItemClass,
  menuIconClass,
  menuTitleClass,
  isMobile,
  asideClass,
} = props;

const isCollapsed = ref(props.isCollapsed);

watch(
  () => isMobile,
  (val) => {
    isCollapsed.value = val;
  },
  { immediate: true }
);

const iconMap = {
  HomeFilled,
  User,
  Notebook,
  Bell,
  Calendar,
  Setting,
};

const authStore = useAuthStore();
const role = computed(() => authStore.user?.role);
type RoleKey = keyof typeof menus;

const menuItems = computed(() => {
  const items = menus[role.value as RoleKey] ?? [];
  return items.map((item) => ({
    ...item,
    icon: iconMap[item.icon as keyof typeof iconMap] ?? HomeFilled,
  }));
});

const route = useRoute();
const activeMenu = computed(() => route.path);

// Function to get icon style based on active menu
const getIconStyle = (item: { route: string }) => ({
  color:
    route.path === item.route
      ? "var(--color-primary)"
      : "var(--menu-text-color)",
});
</script>

<template>
  <el-aside :class="asideClass">
    <div v-if="!isMobile" :class="logoSectionClass">
      <img :src="logoSrc" alt="Logo" class="w-full h-full" />
    </div>
    <el-menu :class="menuClass" :collapse="isCollapsed" router>
      <el-menu-item
        v-for="item in menuItems"
        :key="item.route"
        :index="item.route"
        :title="item.title"
        :class="[
          menuItemClass,
          { 'active-menu-item': activeMenu === item.route },
        ]"
      >
        <el-icon :class="menuIconClass" :style="getIconStyle(item)">
          <component :is="item.icon" />
        </el-icon>
        <template #title>
          <span :class="menuTitleClass">{{ item.title }}</span>
        </template>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>
