import { TargetType, ReportReason, Severity } from "~/types/models/Report";
import { ReportStatus } from "~/types/models/Report";

export interface Report {
  _id?: string;
  reporter_id: string;
  target_id?: string | null;
  target_type: TargetType;
  reason: ReportReason;
  description: string;
  severity: Severity;
  status: ReportStatus;
  created_at: string; // ISO datetime string
}

export class ReportModel implements Report {
  _id?: string;
  reporter_id: string;
  target_id?: string | null;
  target_type: TargetType;
  reason: ReportReason;
  description: string;
  severity: Severity;
  status: ReportStatus;
  created_at: string;


  constructor(data: Partial<Report> = {}) {
    this._id = data._id;
    this.reporter_id = data.reporter_id ?? "";
    this.target_id = data.target_id ?? null;
    this.target_type = data.target_type ?? TargetType.SYSTEM;
    this.reason = data.reason ?? ReportReason.OTHER;
    this.description = data.description ?? "";
    this.severity = data.severity ?? Severity.MEDIUM;
    this.status = data.status ?? ReportStatus.PENDING;
    this.created_at = data.created_at ?? new Date().toISOString();
  }

  toDict() {
    return {
      _id: this._id,
      reporter_id: this.reporter_id,
      target_id: this.target_id,
      target_type: this.target_type,
      reason: this.reason,
      description: this.description,
      severity: this.severity,
      status: this.status,
      created_at: this.created_at,
    };
  }
}
