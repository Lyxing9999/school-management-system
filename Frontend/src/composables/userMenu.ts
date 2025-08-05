import { menus } from "~/constants/menus";

export function useMenu(role: string) {
  if (role === "admin") return menus.admin;
  if (role === "teacher") return menus.teacher;
  if (role === "student") return menus.student;
  return [];
}
