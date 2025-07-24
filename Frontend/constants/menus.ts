// menus.ts - define menus for roles
export const menus = {
  admin: [
    { title: "Dashboard", icon: "HomeFilled", route: "/admin/dashboard" },
    { title: "Manage Users", icon: "User", route: "/admin/manage-user" },
    { title: "Manage Classes", icon: "Notebook", route: "/admin/manage-class" },
    { title: "Notifications", icon: "Bell", route: "/admin/notifications" },
    { title: "System Events", icon: "Calendar", route: "/admin/events" },
    { title: "Settings", icon: "Setting", route: "/admin/settings" },
  ],
  teacher: [
    { title: "Dashboard", icon: "HomeFilled", route: "/teacher/dashboard" },
    { title: "Manage Students", icon: "User", route: "/teacher/students" },
    { title: "My Classes", icon: "Notebook", route: "/teacher/classes" },
    { title: "Attendance", icon: "Calendar", route: "/teacher/attendance" },
    { title: "Notifications", icon: "Bell", route: "/teacher/notifications" },
    { title: "Settings", icon: "Setting", route: "/teacher/settings" },
  ],
  student: [
    { title: "Dashboard", icon: "HomeFilled", route: "/student/dashboard" },
    { title: "My Classes", icon: "Notebook", route: "/student/classes" },
    { title: "Attendance", icon: "Calendar", route: "/student/attendance" },
    { title: "Notifications", icon: "Bell", route: "/student/notifications" },
    { title: "Settings", icon: "Setting", route: "/student/settings" },
    { title: "System Events", icon: "Calendar", route: "/student/events" },
  ],
};
