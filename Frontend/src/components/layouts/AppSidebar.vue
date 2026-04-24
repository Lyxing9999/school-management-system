<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import * as Icons from "@element-plus/icons-vue";
import { useAuthStore } from "~/stores/authStore";
import { ROUTES } from "~/constants/routes";

type RoleKey = keyof typeof ROUTES;

interface MenuItem {
  title: string;
  icon?: keyof typeof Icons;
  route?: string;
  children?: MenuItem[];
  badge?: string; // For "Coming Soon" or "New" badges
}

interface MenuNode extends MenuItem {
  index: string;
  iconComponent: any;
  children?: MenuNode[];
}

type AppRoleKey = Exclude<RoleKey, "AUTH">;

const props = defineProps<{ logoSrc: string; collapsed?: boolean }>();
const emit = defineEmits<{ (e: "navigate"): void }>();

const authStore = useAuthStore();
const route = useRoute();

/** Role menus driven by src/constants/routes.ts */
const menus: Record<AppRoleKey, MenuItem[]> = {
  ADMIN: [
    { title: "Dashboard", icon: "Odometer", route: ROUTES.ADMIN.DASHBOARD },
    {
      title: "Management",
      icon: "Grid",
      children: [
        {
          title: "Users",
          icon: "User",
          route: ROUTES.ADMIN.USERS,
        },
        {
          title: "Classes",
          icon: "Reading",
          route: ROUTES.ADMIN.CLASSES,
        },
        {
          title: "Subjects",
          icon: "Collection",
          route: ROUTES.ADMIN.SUBJECTS,
        },
        {
          title: "Schedules",
          icon: "Calendar",
          route: ROUTES.ADMIN.SCHEDULES,
        },
      ],
    },
    {
      title: "Teaching",
      icon: "Link",
      children: [
        {
          title: "Teaching Assignments",
          icon: "Link",
          route: ROUTES.ADMIN.TEACHING_ASSIGNMENTS,
        },
      ],
    },
    {
      title: "System",
      icon: "Setting",
      children: [
        {
          title: "Notifications",
          icon: "Bell",
          route: ROUTES.ADMIN.NOTIFICATIONS,
        },
        { title: "Events", icon: "Tickets", route: ROUTES.ADMIN.EVENTS },
        { title: "Settings", icon: "Setting", route: ROUTES.ADMIN.SETTINGS },
      ],
    },
  ],

  TEACHER: [
    { title: "Dashboard", icon: "Odometer", route: ROUTES.TEACHER.DASHBOARD },
    {
      title: "Students",
      icon: "UserFilled",
      children: [
        {
          title: "Students",
          icon: "UserFilled",
          route: ROUTES.TEACHER.STUDENTS,
        },
      ],
    },
    {
      title: "Academics",
      icon: "Notebook",
      children: [
        {
          title: "Classes",
          icon: "Notebook",
          route: ROUTES.TEACHER.CLASSES,
        },
        { title: "Grades", icon: "TrendCharts", route: ROUTES.TEACHER.GRADES },
        {
          title: "Attendance",
          icon: "Finished",
          route: ROUTES.TEACHER.ATTENDANCE,
        },
        { title: "Schedule", icon: "Timer", route: ROUTES.TEACHER.SCHEDULE },
      ],
    },
    {
      title: "System",
      icon: "Setting",
      children: [
        {
          title: "Notifications",
          icon: "Bell",
          route: ROUTES.TEACHER.NOTIFICATIONS,
        },
        { title: "Calendar", icon: "Calendar", route: ROUTES.TEACHER.CALENDAR },
        { title: "Settings", icon: "Setting", route: ROUTES.TEACHER.SETTINGS },
      ],
    },
  ],

  STUDENT: [
    { title: "Dashboard", icon: "Odometer", route: ROUTES.STUDENT.DASHBOARD },
    {
      title: "My Study",
      icon: "Notebook",
      children: [
        {
          title: "Enrollments",
          icon: "DocumentAdd",
          route: ROUTES.STUDENT.ENROLLMENTS,
        },
        {
          title: "Classes",
          icon: "Notebook",
          route: ROUTES.STUDENT.CLASSES,
        },
        {
          title: "Grades",
          icon: "TrendCharts",
          route: ROUTES.STUDENT.GRADES,
        },
        {
          title: "Schedule",
          icon: "Timer",
          route: ROUTES.STUDENT.SCHEDULE,
        },
        {
          title: "Attendance",
          icon: "Finished",
          route: ROUTES.STUDENT.ATTENDANCE,
        },
      ],
    },
    {
      title: "System",
      icon: "Setting",
      children: [
        {
          title: "Notifications",
          icon: "Bell",
          route: ROUTES.STUDENT.NOTIFICATIONS,
        },
        { title: "Calendar", icon: "Calendar", route: ROUTES.STUDENT.CALENDAR },
        { title: "Settings", icon: "Setting", route: ROUTES.STUDENT.SETTINGS },
      ],
    },
  ],

  HR_ADMIN: [
    {
      title: "Dashboard",
      icon: "Odometer",
      route: ROUTES.HR_ADMIN.DASHBOARD,
    },
    {
      title: "Employees",
      icon: "UserFilled",
      children: [
        {
          title: "Employee Directory",
          icon: "User",
          route: ROUTES.HR_ADMIN.EMPLOYEES,
        },
        {
          title: "Employee Accounts",
          icon: "Avatar",
          route: ROUTES.HR_ADMIN.EMPLOYEE_ACCOUNTS,
        },
        {
          title: "Archived Employees",
          icon: "FolderDelete",
          route: ROUTES.HR_ADMIN.EMPLOYEE_ARCHIVED,
        },
      ],
    },
    {
      title: "Attendance",
      icon: "Clock",
      children: [
        {
          title: "Overview",
          icon: "List",
          route: ROUTES.HR_ADMIN.ATTENDANCE,
        },
        {
          title: "Wrong Location",
          icon: "Warning",
          route: ROUTES.HR_ADMIN.ATTENDANCE_WRONG_LOCATION,
        },
        {
          title: "Early Leave",
          icon: "Timer",
          route: ROUTES.HR_ADMIN.ATTENDANCE_EARLY_LEAVE,
        },
        {
          title: "Attendance Reports",
          icon: "Document",
          route: ROUTES.HR_ADMIN.ATTENDANCE_REPORTS,
        },
      ],
    },
    {
      title: "Overtime",
      icon: "Timer",
      children: [
        {
          title: "Overview",
          icon: "Timer",
          route: ROUTES.HR_ADMIN.OVERTIME,
        },
        {
          title: "Overtime Reviews",
          icon: "CircleCheck",
          route: ROUTES.HR_ADMIN.OVERTIME_REVIEWS,
        },
        {
          title: "Overtime History",
          icon: "List",
          route: ROUTES.HR_ADMIN.OVERTIME_HISTORY,
        },
      ],
    },
    {
      title: "Leave",
      icon: "Calendar",
      children: [
        {
          title: "Leave Management",
          icon: "Calendar",
          route: ROUTES.HR_ADMIN.LEAVES,
        },
        {
          title: "Leave Reviews",
          icon: "DocumentChecked",
          route: ROUTES.HR_ADMIN.LEAVE_REVIEWS,
        },
        {
          title: "Leave Balances",
          icon: "Coin",
          route: ROUTES.HR_ADMIN.LEAVE_BALANCES,
        },
      ],
    },
    {
      title: "Payroll",
      icon: "Money",
      children: [
        {
          title: "Generate Payroll",
          icon: "Operation",
          route: ROUTES.HR_ADMIN.PAYROLL_GENERATE,
        },
        {
          title: "Payroll Runs",
          icon: "List",
          route: ROUTES.HR_ADMIN.PAYROLL_RUNS,
        },
        {
          title: "Payroll History",
          icon: "List",
          route: ROUTES.HR_ADMIN.PAYROLL_HISTORY,
        },
        {
          title: "Payslips",
          icon: "Document",
          route: ROUTES.HR_ADMIN.PAYSLIPS,
        },
      ],
    },
    {
      title: "Configuration",
      icon: "Setting",
      children: [
        {
          title: "Working Schedules",
          icon: "Clock",
          route: ROUTES.HR_ADMIN.WORKING_SCHEDULES,
        },
        {
          title: "Work Locations",
          icon: "Location",
          route: ROUTES.HR_ADMIN.WORK_LOCATIONS,
        },
        {
          title: "Public Holidays",
          icon: "Calendar",
          route: ROUTES.HR_ADMIN.PUBLIC_HOLIDAYS,
        },
        {
          title: "Deduction Rules",
          icon: "Coin",
          route: ROUTES.HR_ADMIN.DEDUCTION_RULES,
        },
      ],
    },
    {
      title: "Reports",
      icon: "DataAnalysis",
      children: [
        {
          title: "Attendance",
          icon: "Document",
          route: ROUTES.HR_ADMIN.REPORTS_ATTENDANCE,
        },
        {
          title: "Overtime",
          icon: "Document",
          route: ROUTES.HR_ADMIN.REPORTS_OVERTIME,
        },
        {
          title: "Payroll",
          icon: "Document",
          route: ROUTES.HR_ADMIN.REPORTS_PAYROLL,
        },
        {
          title: "Wrong Location",
          icon: "Document",
          route: ROUTES.HR_ADMIN.REPORTS_WRONG_LOCATION,
        },
        {
          title: "Audit Logs",
          icon: "Tickets",
          route: ROUTES.HR_ADMIN.AUDIT_LOGS,
        },
      ],
    },
  ],

  EMPLOYEE: [
    {
      title: "Dashboard",
      icon: "Odometer",
      route: ROUTES.EMPLOYEE.DASHBOARD,
    },
    {
      title: "Attendance",
      icon: "Clock",
      children: [
        {
          title: "Today",
          icon: "Clock",
          route: ROUTES.EMPLOYEE.ATTENDANCE_TODAY,
        },
        {
          title: "Attendance History",
          icon: "List",
          route: ROUTES.EMPLOYEE.ATTENDANCE_HISTORY,
        },
      ],
    },
    {
      title: "Overtime",
      icon: "Timer",
      children: [
        {
          title: "Request Overtime",
          icon: "EditPen",
          route: ROUTES.EMPLOYEE.OVERTIME_REQUEST,
        },
        {
          title: "Overtime History",
          icon: "Document",
          route: ROUTES.EMPLOYEE.OVERTIME_HISTORY,
        },
      ],
    },
    {
      title: "Leave",
      icon: "Calendar",
      children: [
        {
          title: "Request Leave",
          icon: "EditPen",
          route: ROUTES.EMPLOYEE.LEAVE_REQUEST,
        },
        {
          title: "Leave History",
          icon: "Document",
          route: ROUTES.EMPLOYEE.LEAVE_HISTORY,
        },
        {
          title: "Leave Balance",
          icon: "Memo",
          route: ROUTES.EMPLOYEE.LEAVE_BALANCE,
        },
      ],
    },
    {
      title: "Payroll",
      icon: "Money",
      children: [
        {
          title: "Payslips",
          icon: "Document",
          route: ROUTES.EMPLOYEE.PAYSLIPS,
        },
      ],
    },
    {
      title: "Profile",
      icon: "User",
      route: ROUTES.EMPLOYEE.PROFILE,
    },
  ],

  MANAGER: [
    {
      title: "Dashboard",
      icon: "Odometer",
      route: ROUTES.MANAGER.DASHBOARD,
    },
    {
      title: "Attendance",
      icon: "Clock",
      children: [
        {
          title: "Team Attendance",
          icon: "UserFilled",
          route: ROUTES.MANAGER.ATTENDANCE_TEAM,
        },
        {
          title: "Attendance Reports",
          icon: "Document",
          route: ROUTES.MANAGER.ATTENDANCE_REPORTS,
        },
        {
          title: "Early Leave",
          icon: "Timer",
          route: ROUTES.MANAGER.ATTENDANCE_EARLY_LEAVE,
        },
      ],
    },
    {
      title: "Overtime",
      icon: "Timer",
      children: [
        {
          title: "OT Reviews",
          icon: "CircleCheck",
          route: ROUTES.MANAGER.OVERTIME_REVIEWS,
        },
        {
          title: "OT History",
          icon: "Document",
          route: ROUTES.MANAGER.OVERTIME_HISTORY,
        },
      ],
    },
    {
      title: "Leave",
      icon: "Calendar",
      children: [
        {
          title: "Leave Reviews",
          icon: "CircleCheck",
          route: ROUTES.MANAGER.LEAVE_REVIEWS,
        },
        {
          title: "Leave History",
          icon: "Document",
          route: ROUTES.MANAGER.LEAVE_HISTORY,
        },
      ],
    },
    {
      title: "Reports",
      icon: "DataAnalysis",
      children: [
        {
          title: "Team Reports",
          icon: "Document",
          route: ROUTES.MANAGER.REPORTS_TEAM,
        },
        {
          title: "Audit Logs",
          icon: "Tickets",
          route: ROUTES.MANAGER.AUDIT_LOGS,
        },
      ],
    },
  ],

  PAYROLL_MANAGER: [
    {
      title: "Dashboard",
      icon: "Odometer",
      route: ROUTES.PAYROLL_MANAGER.DASHBOARD,
    },
    {
      title: "Payroll",
      icon: "Money",
      children: [
        {
          title: "Generate Payroll",
          icon: "Operation",
          route: ROUTES.PAYROLL_MANAGER.PAYROLL_GENERATE,
        },
        {
          title: "Payroll Runs",
          icon: "List",
          route: ROUTES.PAYROLL_MANAGER.PAYROLL_RUNS,
        },
        {
          title: "Payslips",
          icon: "Document",
          route: ROUTES.PAYROLL_MANAGER.PAYSLIPS,
        },
      ],
    },
    {
      title: "Attendance",
      icon: "Clock",
      children: [
        {
          title: "Final Attendance",
          icon: "List",
          route: ROUTES.PAYROLL_MANAGER.ATTENDANCE_FINAL,
        },
      ],
    },
    {
      title: "Overtime",
      icon: "Timer",
      children: [
        {
          title: "Approved OT",
          icon: "CircleCheck",
          route: ROUTES.PAYROLL_MANAGER.OVERTIME_APPROVED,
        },
      ],
    },
    {
      title: "Reports",
      icon: "DataAnalysis",
      children: [
        {
          title: "Payroll Reports",
          icon: "Document",
          route: ROUTES.PAYROLL_MANAGER.REPORTS_PAYROLL,
        },
      ],
    },
  ],
};

/** IMPORTANT: don’t default to ADMIN while loading */
const role = computed<RoleKey | null>(() => {
  if (!authStore.isReady) return null;
  const r = authStore.user?.role?.toUpperCase();
  return (r as RoleKey) ?? null;
});

function iconOf(name?: keyof typeof Icons) {
  if (!name) return Icons.Menu;
  return (Icons as any)[name] ?? Icons.Menu;
}

/** stable submenu indexes */
function groupIndex(path: string[], title: string) {
  return `group:${[...path, title].join(" / ")}`;
}

function toNodes(items: MenuItem[], path: string[] = []): MenuNode[] {
  return items.map((it) => {
    const index = it.route || groupIndex(path, it.title);
    return {
      ...it,
      index,
      iconComponent: iconOf(it.icon),
      children: it.children
        ? toNodes(it.children, [...path, it.title])
        : undefined,
    };
  });
}

const menuTree = computed<MenuNode[]>(() => {
  if (!role.value) return [];
  if (role.value === "AUTH") return [];
  return toNodes(menus[role.value]);
});

/** active leaf route */
function matchActiveLeaf(items: MenuNode[]): string {
  for (const it of items) {
    if (
      it.route &&
      (route.path === it.route || route.path.startsWith(it.route + "/"))
    )
      return it.route;
    if (it.children?.length) {
      const hit = matchActiveLeaf(it.children);
      if (hit) return hit;
    }
  }
  return "";
}

const activeIndex = computed(() => matchActiveLeaf(menuTree.value));

/** open parent groups */
function findOpenGroups(items: MenuNode[], parents: string[] = []): string[] {
  for (const it of items) {
    if (
      it.route &&
      (route.path === it.route || route.path.startsWith(it.route + "/"))
    )
      return parents;
    if (it.children?.length) {
      const res = findOpenGroups(it.children, [...parents, it.index]);
      if (res.length) return res;
    }
  }
  return [];
}

const openeds = computed(() => findOpenGroups(menuTree.value));

function handleSelect() {
  emit("navigate");
}
</script>

<!-- Sidebar is now always visible on all screens. Mobile navigation is handled by this sidebar. -->
<template>
  <aside class="app-aside" :class="{ 'is-collapsed': !!collapsed }">
    <div class="logo-section">
      <div class="logo-badge" aria-label="App logo">
        <img :src="logoSrc" class="logo-image" alt="Logo" />
      </div>
    </div>

    <div class="menu-scroll">
      <el-menu
        v-if="authStore.isReady && role"
        class="app-menu"
        router
        :collapse="!!collapsed"
        :collapse-transition="false"
        :default-active="activeIndex"
        :default-openeds="openeds"
        @select="handleSelect"
      >
        <template v-for="item in menuTree" :key="item.index">
          <el-sub-menu v-if="item.children?.length" :index="item.index">
            <template #title>
              <el-icon><component :is="item.iconComponent" /></el-icon>
              <span class="menu-title">{{ item.title }}</span>
            </template>

            <el-menu-item
              v-for="child in item.children"
              :key="child.index"
              :index="child.route!"
              :title="child.title"
            >
              <el-icon><component :is="child.iconComponent" /></el-icon>
              <template #title>
                <span class="menu-title">{{ child.title }}</span>
                <el-tag
                  v-if="child.badge"
                  size="small"
                  type="warning"
                  class="menu-badge"
                >
                  {{ child.badge }}
                </el-tag>
              </template>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item v-else :index="item.route!" :title="item.title">
            <el-icon><component :is="item.iconComponent" /></el-icon>
            <template #title>
              <span class="menu-title">{{ item.title }}</span>
              <el-tag
                v-if="item.badge"
                size="small"
                type="warning"
                class="menu-badge"
              >
                {{ item.badge }}
              </el-tag>
            </template>
          </el-menu-item>
        </template>
      </el-menu>

      <!-- Skeleton while auth loads -->
      <div v-else class="menu-skeleton" aria-busy="true">
        <div class="skeleton-item" v-for="i in 7" :key="i"></div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* sidebar.scss (imported globally via nuxt.config) owns all .app-aside
   and .app-menu rules using the real design tokens.
   This block only adds what sidebar.scss does not cover. */

.menu-skeleton .skeleton-item {
  background: color-mix(in srgb, var(--muted-color) 25%, transparent);
  height: 36px;
  border-radius: 9999px;
  margin: 6px 0;
}

.menu-badge {
  margin-left: 8px;
  font-size: 10px;
  padding: 0 6px;
  height: 18px;
  line-height: 18px;
}
</style>
