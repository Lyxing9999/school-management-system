export const ROUTES = {
  AUTH: {
    LOGIN: "/auth/login",
    FORGOT_PASSWORD: "/auth/forgot-password",
    RESET_PASSWORD: "/auth/reset-password",
  },

  // ============================================
  // SCHOOL MANAGEMENT
  // ============================================
  ADMIN: {
    DASHBOARD: "/admin/dashboard",

    USERS: "/admin/manage-user",
    CLASSES: "/admin/manage-class",
    SUBJECTS: "/admin/manage-subject",
    SCHEDULES: "/admin/manage-schedule",
    TEACHING_ASSIGNMENTS: "/admin/teaching-assignments",

    NOTIFICATIONS: "/admin/notifications",
    EVENTS: "/admin/events",
    SETTINGS: "/admin/settings",
  },

  TEACHER: {
    DASHBOARD: "/teacher/dashboard",

    STUDENTS: "/teacher/students",
    CLASSES: "/teacher/classes",
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
    CLASSES: "/student/classes",
    GRADES: "/student/grades",
    SCHEDULE: "/student/schedule",
    ATTENDANCE: "/student/attendance",

    CALENDAR: "/student/calendar",
    NOTIFICATIONS: "/student/notifications",
    SETTINGS: "/student/settings",
  },

  // ============================================
  // HRMS
  // ============================================
  HR_ADMIN: {
    DASHBOARD: "/hr",

    EMPLOYEES: "/hr/employees",
    EMPLOYEE_DETAIL: (id: string) => `/hr/employees/${id}`,
    EMPLOYEE_ACCOUNTS: "/hr/employees/accounts",
    EMPLOYEE_ARCHIVED: "/hr/employees/archived",

    ATTENDANCE: "/hr/attendance",
    ATTENDANCE_WRONG_LOCATION: "/hr/attendance/wrong-location",
    ATTENDANCE_REPORTS: "/hr/attendance/reports",

    OVERTIME: "/hr/overtime",
    OVERTIME_DETAIL: (id: string) => `/hr/overtime/${id}`,
    OVERTIME_REVIEWS: "/hr/overtime/reviews",
    OVERTIME_HISTORY: "/hr/overtime/history",

    LEAVES: "/hr/leaves",
    LEAVE_DETAIL: (id: string) => `/hr/leaves/${id}`,
    LEAVE_REVIEWS: "/hr/leaves/reviews",
    LEAVE_BALANCES: "/hr/leaves/balances",

    PAYROLL_RUNS: "/hr/payroll/runs",
    PAYROLL_GENERATE: "/hr/payroll/runs/generate",
    PAYSLIPS: "/hr/payroll/payslips",
    PAYROLL_HISTORY: "/hr/payroll/history",

    WORKING_SCHEDULES: "/hr/config/schedules",
    WORK_LOCATIONS: "/hr/config/work-locations",
    PUBLIC_HOLIDAYS: "/hr/config/public-holidays",
    DEDUCTION_RULES: "/hr/config/deduction-rules",

    REPORTS_ATTENDANCE: "/hr/reports/attendance",
    REPORTS_OVERTIME: "/hr/reports/overtime",
    REPORTS_PAYROLL: "/hr/reports/payroll",
    REPORTS_WRONG_LOCATION: "/hr/reports/wrong-location",
    AUDIT_LOGS: "/hr/audit",
    SETTINGS: "/hr/settings",
  },

  EMPLOYEE: {
    DASHBOARD: "/employee/dashboard",
    PROFILE: "/employee/profile",

    ATTENDANCE_TODAY: "/employee/attendance/today",
    ATTENDANCE_HISTORY: "/employee/attendance/history",

    OVERTIME_REQUEST: "/employee/overtime/request",
    OVERTIME_HISTORY: "/employee/overtime/history",
    OVERTIME_DETAIL: (id: string) => `/employee/overtime/${id}`,

    LEAVE_REQUEST: "/employee/leaves/request",
    LEAVE_HISTORY: "/employee/leaves/history",
    LEAVE_BALANCE: "/employee/leaves/balance",
    LEAVE_DETAIL: (id: string) => `/employee/leaves/${id}`,

    PAYSLIPS: "/employee/payslips",
    PAYSLIP_DETAIL: (id: string) => `/employee/payslips/${id}`,
    SETTINGS: "/employee/settings",
  },

  MANAGER: {
    DASHBOARD: "/manager/dashboard",

    ATTENDANCE_TEAM: "/manager/attendance/team",
    ATTENDANCE_REPORTS: "/manager/attendance/reports",

    OVERTIME_REVIEWS: "/manager/overtime/reviews",
    OVERTIME_HISTORY: "/manager/overtime/history",
    OVERTIME_DETAIL: (id: string) => `/manager/overtime/${id}`,

    LEAVE_REVIEWS: "/manager/leaves/reviews",
    LEAVE_HISTORY: "/manager/leaves/history",
    LEAVE_DETAIL: (id: string) => `/manager/leaves/${id}`,
    AUDIT_LOGS: "/manager/audit",

    REPORTS_TEAM: "/manager/reports/team",
    SETTINGS: "/manager/settings",
  },

  PAYROLL_MANAGER: {
    DASHBOARD: "/payroll/dashboard",

    ATTENDANCE_FINAL: "/payroll/attendance/final",

    OVERTIME_APPROVED: "/payroll/overtime/approved",
    OVERTIME_DETAIL: (id: string) => `/payroll/overtime/${id}`,

    PAYROLL_GENERATE: "/payroll/runs/generate",
    PAYROLL_RUNS: "/payroll/runs",
    PAYSLIPS: "/payroll/payslips",
    PAYSLIP_DETAIL: (id: string) => `/payroll/payslips/${id}`,

    REPORTS_PAYROLL: "/payroll/reports",
    SETTINGS: "/payroll/settings",
  },
} as const;
