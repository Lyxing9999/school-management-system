// All roles in the system
export enum Role {
  ADMIN = "admin",
  TEACHER = "teacher",
  STUDENT = "student",
  FRONT_OFFICE = "front_office",
  PARENT = "parent",
  ACADEMIC = "academic",
  FINANCE = "finance",
  HR = "hr",
}

// Non-staff users
export enum UserRole {
  STUDENT = "student",
  PARENT = "parent",
}

// Staff members
export enum StaffRole {
  TEACHER = "teacher",
  ACADEMIC = "academic",
}

// Arrays for easy checks
export const AllRoles: Role[] = [
  Role.ADMIN,
  Role.TEACHER,
  Role.STUDENT,
  Role.FRONT_OFFICE,
  Role.PARENT,
  Role.ACADEMIC,
  Role.FINANCE,
  Role.HR,
];

export const AllUserRoles: UserRole[] = [UserRole.STUDENT, UserRole.PARENT];

export const AllStaffRoles: StaffRole[] = [
  StaffRole.TEACHER,
  StaffRole.ACADEMIC,
];
