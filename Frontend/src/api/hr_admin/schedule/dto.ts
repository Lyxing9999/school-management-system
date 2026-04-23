// frontend/src/api/hr_admin/schedule/schedule.dto.ts
import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export interface WorkingScheduleDTO {
  id: string;
  name: string;
  schedule_name?: string | null;
  start_time: string; // HH:MM:SS
  end_time: string; // HH:MM:SS
  working_days: number[]; // 0=Monday, 6=Sunday
  weekend_days: number[];
  total_hours_per_day: number;
  is_default: boolean;
  created_by: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  lifecycle: LifecycleDTO;
}

export interface WorkingScheduleCreateDTO {
  name: string;
  start_time: string;
  end_time: string;
  working_days: number[];
  weekend_days?: number[];
  total_hours_per_day?: number;
  is_default?: boolean;
}

export interface WorkingScheduleUpdateDTO {
  name?: string;
  start_time?: string;
  end_time?: string;
  working_days?: number[];
  weekend_days?: number[];
  total_hours_per_day?: number;
  is_default?: boolean;
}

export interface WorkingScheduleListParams {
  signal?: AbortSignal;
}
