export const ROUTES = {
  ADMIN: {
    DASHBOARD: "/admin/dashboard",
    MANAGE_USERS: "/admin/manage-user",
    MANAGE_CLASSES: "/admin/manage-class",
    TEACHING_ASSIGNMENTS: "/admin/teaching-assignments",
    MANAGE_SUBJECTS: "/admin/manage-subject",
    MANAGE_SCHEDULES: "/admin/manage-schedule",
    NOTIFICATIONS: "/admin/notifications",
    SYSTEM_EVENTS: "/admin/events",
    SETTINGS: "/admin/settings",
  },
  TEACHER: {
    DASHBOARD: "/teacher/dashboard",
    MANAGE_STUDENTS: "/teacher/students",
    MY_CLASSES: "/teacher/classes",
    GRADES: "/teacher/grades",
    SCHEDULE: "/teacher/schedule",
    ATTENDANCE: "/teacher/attendance",
    CALENDAR: "/teacher/calendar",
    NOTIFICATIONS: "/teacher/notifications",
    SETTINGS: "/teacher/settings",
  },
  STUDENT: {
    DASHBOARD: "/student/dashboard",
    ENROLLMENTS: "/student/enrollments",
    MY_CLASSES: "/student/classes",
    MY_GRADES: "/student/grades",
    MY_SCHEDULE: "/student/schedule",
    ATTENDANCE: "/student/attendance",
    EVENTS: "/student/events",
    NOTIFICATIONS: "/student/notifications",
    SETTINGS: "/student/settings",
  },
} as const;

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES][keyof unknown];
