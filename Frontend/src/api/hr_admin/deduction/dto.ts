import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export type DeductionRuleType = "late" | "early_leave" | "absent";

/**
 * Deduction rule data transfer object
 */
export interface DeductionRuleDTO {
  id: string;
  type: DeductionRuleType | string;
  min_minutes: number;
  max_minutes: number | null;
  deduction_percentage: number;
  is_active: boolean;
  created_by: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  lifecycle: LifecycleDTO;
}

/**
 * DTO for creating a deduction rule
 * POST /api/hrms/deduction-rules
 */
export interface DeductionRuleCreateDTO {
  type: DeductionRuleType | string;
  min_minutes: number;
  max_minutes?: number | null;
  deduction_percentage: number;
  is_active?: boolean;
}

/**
 * DTO for updating a deduction rule
 * PATCH /api/hrms/deduction-rules/<rule_id>
 */
export interface DeductionRuleUpdateDTO {
  min_minutes?: number | null;
  max_minutes?: number | null;
  deduction_percentage?: number | null;
  is_active?: boolean | null;
}

/**
 * List parameters for deduction rules
 * GET /api/hrms/deduction-rules
 */
export interface DeductionRuleListParams {
  type?: DeductionRuleType | string;
  is_active?: boolean;
  include_deleted?: boolean;
  deleted_only?: boolean;
  page?: number;
  limit?: number;
  signal?: AbortSignal;
}

/**
 * Query parameters for applicable deduction rule
 * GET /api/hrms/deduction-rules/applicable
 */
export interface DeductionRuleApplicableParams {
  type: DeductionRuleType | string;
  minutes: number;
  signal?: AbortSignal;
}

/**
 * Paginated deduction rule list response
 */
export interface DeductionRuleListResponseDTO {
  items: DeductionRuleDTO[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
