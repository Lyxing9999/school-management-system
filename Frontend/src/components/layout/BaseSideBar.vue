<!-- components/layout/AppSidebar.vue -->
<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "~/stores/authStore";
import schoolLogo from "~/assets/image/school-logo.jpg";
import * as Icons from "@element-plus/icons-vue";
import { ROUTES } from "~/constants/routes";

type RoleKey = keyof typeof ROUTES;

interface MenuItem {
  title: string;
  icon: keyof typeof Icons;
  route: string;
}

const menus: Record<RoleKey, MenuItem[]> = {
  ADMIN: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.ADMIN.DASHBOARD },
    { title: "Manage Users", icon: "User", route: ROUTES.ADMIN.MANAGE_USERS },
    {
      title: "Manage Classes",
      icon: "Notebook",
      route: ROUTES.ADMIN.MANAGE_CLASSES,
    },
    {
      title: "Manage Subjects",
      icon: "Document",
      route: ROUTES.ADMIN.MANAGE_SUBJECTS,
    },
    {
      title: "Manage Schedules",
      icon: "Document",
      route: ROUTES.ADMIN.MANAGE_SCHEDULES,
    },
    { title: "Notifications", icon: "Bell", route: ROUTES.ADMIN.NOTIFICATIONS },
    {
      title: "System Events",
      icon: "Calendar",
      route: ROUTES.ADMIN.SYSTEM_EVENTS,
    },
    { title: "Settings", icon: "Setting", route: ROUTES.ADMIN.SETTINGS },
  ],
  TEACHER: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.TEACHER.DASHBOARD },
    { title: "My Classes", icon: "Notebook", route: ROUTES.TEACHER.MY_CLASSES },
    {
      title: "My Students",
      icon: "User",
      route: ROUTES.TEACHER.MANAGE_STUDENTS,
    },
    {
      title: "Schedule",
      icon: "Calendar",
      route: ROUTES.TEACHER.SCHEDULE,
    },
    { title: "Grades", icon: "Document", route: ROUTES.TEACHER.GRADES },
    { title: "Attendance", icon: "Calendar", route: ROUTES.TEACHER.ATTENDANCE },
    { title: "Events", icon: "Calendar", route: ROUTES.TEACHER.EVENTS },
    {
      title: "Notifications",
      icon: "Bell",
      route: ROUTES.TEACHER.NOTIFICATIONS,
    },
    { title: "Settings", icon: "Setting", route: ROUTES.TEACHER.SETTINGS },
  ],
  STUDENT: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.STUDENT.DASHBOARD },

    { title: "My Classes", icon: "Notebook", route: ROUTES.STUDENT.MY_CLASSES },
    { title: "My Grades", icon: "Document", route: ROUTES.STUDENT.MY_GRADES },
    {
      title: "My Schedule",
      icon: "DateTime",
      route: ROUTES.STUDENT.MY_SCHEDULE,
    },
    { title: "Attendance", icon: "Calendar", route: ROUTES.STUDENT.ATTENDANCE },
    {
      title: "Notifications",
      icon: "Bell",
      route: ROUTES.STUDENT.NOTIFICATIONS,
    },
    { title: "Settings", icon: "Setting", route: ROUTES.STUDENT.SETTINGS },
  ],
  ACADEMIC: [
    {
      title: "Dashboard",
      icon: "HomeFilled",
      route: ROUTES.ACADEMIC.DASHBOARD,
    },
    {
      title: "My Classes",
      icon: "Notebook",
      route: ROUTES.ACADEMIC.MY_CLASSES,
    },
    {
      title: "Manage Students",
      icon: "User",
      route: ROUTES.ACADEMIC.STUDENTS,
    },

    {
      title: "Attendance",
      icon: "Calendar",
      route: ROUTES.ACADEMIC.ATTENDANCE,
    },
    {
      title: "Notifications",
      icon: "Bell",
      route: ROUTES.ACADEMIC.NOTIFICATIONS,
    },
  ],
  FRONT_OFFICE: [
    {
      title: "Dashboard",
      icon: "HomeFilled",
      route: ROUTES.FRONT_OFFICE.DASHBOARD,
    },
    {
      title: "Manage Visits",
      icon: "User",
      route: ROUTES.FRONT_OFFICE.MANAGE_VISITS,
    },
    {
      title: "Notifications",
      icon: "Bell",
      route: ROUTES.FRONT_OFFICE.NOTIFICATIONS,
    },
    { title: "Settings", icon: "Setting", route: ROUTES.FRONT_OFFICE.SETTINGS },
  ],
  FINANCE: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.FINANCE.DASHBOARD },
    { title: "Payments", icon: "Money", route: ROUTES.FINANCE.PAYMENTS },
    { title: "Reports", icon: "Document", route: ROUTES.FINANCE.REPORTS },
    { title: "Settings", icon: "Setting", route: ROUTES.FINANCE.SETTINGS },
  ],
  PARENT: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.PARENT.DASHBOARD },
    { title: "Children", icon: "User", route: ROUTES.PARENT.CHILDREN },
    { title: "Attendance", icon: "Calendar", route: ROUTES.PARENT.ATTENDANCE },
    {
      title: "Notifications",
      icon: "Bell",
      route: ROUTES.PARENT.NOTIFICATIONS,
    },
    { title: "Settings", icon: "Setting", route: ROUTES.PARENT.SETTINGS },
  ],
  HR: [
    { title: "Dashboard", icon: "HomeFilled", route: ROUTES.HR.DASHBOARD },
    { title: "Employees", icon: "User", route: ROUTES.HR.EMPLOYEES },
    { title: "Notifications", icon: "Bell", route: ROUTES.HR.NOTIFICATIONS },
    { title: "Settings", icon: "Setting", route: ROUTES.HR.SETTINGS },
  ],
};

const authStore = useAuthStore();
const route = useRoute();

const role = computed<RoleKey | null>(() => {
  const r = authStore.user?.role;
  if (!r) return null;
  return r.toUpperCase() as RoleKey;
});

const menuItems = computed(() => {
  return (
    menus[role.value ?? "ADMIN"]?.map((item) => ({
      ...item,
      iconComponent: Icons[item.icon] ?? Icons.HomeFilled,
    })) ?? []
  );
});

const activeMenu = computed(
  () =>
    menuItems.value.find((item) => route.path.startsWith(item.route))?.route ??
    ""
);
</script>

<template>
  <el-aside width="240px" class="app-aside">
    <div class="logo-section">
      <img :src="schoolLogo" alt="Logo" class="logo-image" />
    </div>

    <el-menu router :default-active="activeMenu" class="app-menu">
      <el-menu-item
        v-for="item in menuItems"
        :key="item.route"
        :index="item.route"
        :title="item.title"
        :class="{ 'active-menu-item': activeMenu === item.route }"
      >
        <el-icon>
          <component :is="item.iconComponent" />
        </el-icon>
        <template #title>
          <span>{{ item.title }}</span>
        </template>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<style scoped lang="scss">
.app-aside {
  background-color: var(--color-card);
  backdrop-filter: blur(10px);
  box-shadow: 2px 0 6px rgba(0, 0, 0, 0.06);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
}

.logo-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 1rem 0.75rem;
}

.logo-image {
  max-width: 160px;
  border-radius: 8px;
}

.app-menu {
  border-right: none;
  padding: 0.25rem 0.5rem 0.75rem;
}

.el-menu-item {
  border-radius: 9999px;
  margin: 0.25rem 0;
  padding: 0.5rem 1rem !important;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  color: #4b5563;
  border: 1px solid transparent;
}

.el-menu-item:hover {
  border-color: var(--color-primary-light-4);
  background-color: var(--color-primary-light-9);
  color: var(--color-primary);
}

.active-menu-item {
  border-color: var(--color-primary);
  background-color: rgba(126, 87, 194, 0.12);
}

.active-menu-item::after {
  display: none;
}

.active-menu-item .el-icon,
.active-menu-item span {
  color: var(--color-primary);
}
</style>
