import { Role } from "~/api/types/enums/role.enum";
export const roleUserOptions: { value: Role; label: string }[] = [
  { value: Role.STUDENT, label: "Student" },
  { value: Role.PARENT, label: "Parent" },
];

export const roleStaffOptions: { value: Role; label: string }[] = [
  { value: Role.ACADEMIC, label: "Academic" },
  { value: Role.TEACHER, label: "Teacher" },
];

export const roleOptions: { value: Role; label: string }[] = [
  { value: Role.STUDENT, label: "Student" },
  { value: Role.PARENT, label: "Parent" },
  { value: Role.ACADEMIC, label: "Academic" },
  { value: Role.TEACHER, label: "Teacher" },
];
