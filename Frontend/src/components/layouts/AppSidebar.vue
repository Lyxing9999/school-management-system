<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import * as Icons from "@element-plus/icons-vue";
import { useAuthStore } from "~/stores/authStore";
import { ROUTES } from "~/constants/routes";

type RoleKey = keyof typeof ROUTES;

interface MenuItem {
  title: string;
  icon: keyof typeof Icons;
  route: string;
}

defineProps<{ logoSrc: string }>();
const emit = defineEmits<{ (e: "navigate"): void }>();

const authStore = useAuthStore();
const route = useRoute();

const menus: Record<RoleKey, MenuItem[]> = {
  ADMIN: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.ADMIN.DASHBOARD },
    {
      title: "Manage Users",
      icon: "Management",
      route: ROUTES.ADMIN.MANAGE_USERS,
    },
    {
      title: "Manage Classes",
      icon: "Notebook",
      route: ROUTES.ADMIN.MANAGE_CLASSES,
    },
    {
      title: "Teaching Assignments",
      icon: "Link",
      route: ROUTES.ADMIN.TEACHING_ASSIGNMENTS,
    },
    {
      title: "Manage Subjects",
      icon: "Collection",
      route: ROUTES.ADMIN.MANAGE_SUBJECTS,
    },
    {
      title: "Manage Schedules",
      icon: "Calendar",
      route: ROUTES.ADMIN.MANAGE_SCHEDULES,
    },
    {
      title: "System Events",
      icon: "Tickets",
      route: ROUTES.ADMIN.SYSTEM_EVENTS,
    },
    { title: "Notifications", icon: "Bell", route: ROUTES.ADMIN.NOTIFICATIONS },
    { title: "Settings", icon: "Setting", route: ROUTES.ADMIN.SETTINGS },
  ],
  TEACHER: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.TEACHER.DASHBOARD },
    {
      title: "Manage Students",
      icon: "UserFilled",
      route: ROUTES.TEACHER.MANAGE_STUDENTS,
    },
    { title: "My Classes", icon: "Notebook", route: ROUTES.TEACHER.MY_CLASSES },
    { title: "Grades", icon: "TrendCharts", route: ROUTES.TEACHER.GRADES },
    { title: "Attendance", icon: "Finished", route: ROUTES.TEACHER.ATTENDANCE },
    { title: "Schedule", icon: "Timer", route: ROUTES.TEACHER.SCHEDULE },
    {
      title: "Notifications",
      icon: "Bell",
      route: ROUTES.TEACHER.NOTIFICATIONS,
    },
    { title: "Calendar", icon: "Calendar", route: ROUTES.TEACHER.CALENDAR },
    { title: "Settings", icon: "Setting", route: ROUTES.TEACHER.SETTINGS },
  ],
  STUDENT: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.STUDENT.DASHBOARD },
    { title: "My Classes", icon: "Notebook", route: ROUTES.STUDENT.MY_CLASSES },
    {
      title: "My Grades",
      icon: "TrendCharts",
      route: ROUTES.STUDENT.MY_GRADES,
    },
    { title: "My Schedule", icon: "Timer", route: ROUTES.STUDENT.MY_SCHEDULE },
    { title: "Attendance", icon: "Finished", route: ROUTES.STUDENT.ATTENDANCE },
    { title: "Events", icon: "Calendar", route: ROUTES.STUDENT.EVENTS },
    {
      title: "Notifications",
      icon: "Bell",
      route: ROUTES.STUDENT.NOTIFICATIONS,
    },
    { title: "Settings", icon: "Setting", route: ROUTES.STUDENT.SETTINGS },
  ],
};

// IMPORTANT: do NOT default to ADMIN while loading
const role = computed<RoleKey | null>(() => {
  if (!authStore.isReady) return null;
  const r = authStore.user?.role?.toUpperCase();
  return (r as RoleKey) ?? null;
});

const menuItems = computed(() => {
  if (!role.value) return [];
  const list = menus[role.value] ?? [];
  return list.map((item) => ({
    ...item,
    iconComponent: Icons[item.icon] ?? Icons.HomeFilled,
  }));
});

const activeMenu = computed(() => {
  const hit = menuItems.value.find(
    (item) =>
      route.path === item.route || route.path.startsWith(item.route + "/")
  );
  return hit?.route ?? "";
});

function handleSelect() {
  emit("navigate");
}
</script>

<template>
  <div class="app-aside">
    <div class="logo-section">
      <div class="logo-badge">
        <img :src="logoSrc" class="logo-image" alt="Logo" />
      </div>
    </div>

    <div class="menu-scroll">
      <el-menu
        v-if="authStore.isReady && role"
        router
        :default-active="activeMenu"
        class="app-menu"
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.route"
          :index="item.route"
          :title="item.title"
          :class="{ 'active-menu-item': activeMenu === item.route }"
        >
          <el-icon><component :is="item.iconComponent" /></el-icon>

          <template #title>
            <span class="menu-title">{{ item.title }}</span>
          </template>
        </el-menu-item>
      </el-menu>

      <div v-else class="menu-skeleton">
        <div class="skeleton-item" v-for="i in 6" :key="i"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-aside {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo-section {
  padding: 12px;
}
.logo-badge {
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo-image {
  width: 120px;
  height: auto;
  display: block;
}

.menu-scroll {
  flex: 1 1 auto;
  overflow: auto;
  padding: 0 8px;
}

/* --- IMPORTANT: prevent long menu text from wrapping --- */
/* Make Element Plus title area shrinkable inside flex row */
:deep(.app-menu .el-menu-item__title) {
  flex: 1 1 auto;
  min-width: 0; /* KEY for ellipsis to work inside flex */
}

/* Your label: single line + ellipsis */
.menu-title {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Optional: also avoid any overflow from the menu item row */
:deep(.app-menu .el-menu-item) {
  overflow: hidden;
}
/* ------------------------------------------------------ */

.menu-skeleton {
  padding: 8px 4px;
  display: grid;
  gap: 10px;
}
.skeleton-item {
  height: 34px;
  border-radius: 10px;
  background: rgba(148, 163, 184, 0.25);
}
</style>
