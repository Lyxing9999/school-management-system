export enum StudentStatus {
  ACTIVE = "active",
  SUSPENDED = "suspended",
  DROPPED_OUT = "dropped_out",
  GRADUATED = "graduated",
  ARCHIVED = "archived",
}

export const StudentStatusLabel: Record<StudentStatus, string> = {
  [StudentStatus.ACTIVE]: "Active",
  [StudentStatus.SUSPENDED]: "Suspended",
  [StudentStatus.DROPPED_OUT]: "Dropped Out",
  [StudentStatus.GRADUATED]: "Graduated",
  [StudentStatus.ARCHIVED]: "Archived",
};
