import type { NotifType } from "~/api/notifications/notification.dto";

export const NOTIF_TYPE_OPTIONS: { label: string; value: NotifType }[] = [
  { label: "Class Assigned", value: "CLASS_ASSIGNMENT" },
  { label: "Class Unassigned", value: "CLASS_UNASSIGNED" },
  { label: "Class Enrolled", value: "CLASS_ENROLLED" },
  { label: "Class Removed", value: "CLASS_REMOVED" },
  { label: "Schedule Assigned", value: "SCHEDULE_ASSIGNED" },
  { label: "Schedule Updated", value: "SCHEDULE_UPDATED" },
  { label: "Grade Published", value: "GRADE_PUBLISHED" },
  { label: "Announcement", value: "ANNOUNCEMENT" },
];
