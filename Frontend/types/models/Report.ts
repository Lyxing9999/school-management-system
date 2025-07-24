export enum TargetType {
  STUDENT = "student",
  TEACHER = "teacher",
  CLASS = "class",
  SYSTEM = "system",
  CONTENT = "content",
}

export enum ReportReason {
  BUG = "bug",
  ABUSE = "abuse",
  INAPPROPRIATE_CONTENT = "inappropriate_content",
  UNFAIR_TREATMENT = "unfair_treatment",
  ERROR = "error",
  OTHER = "other",
}

export enum Severity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
}

export enum ReportStatus {
  PENDING = "pending",
  REVIEWED = "reviewed",
  RESOLVED = "resolved",
}

export interface Report {
  _id?: string;
  reporter_id: string;
  target_id?: string | null;
  target_type: TargetType;
  reason: ReportReason;
  description: string;
  severity?: Severity;
  status?: ReportStatus;
}
