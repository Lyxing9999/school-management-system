import type { LifecycleDTO } from "~/api/types/lifecycle.dto";

export interface PublicHolidayDTO {
  id: string;
  name: string;
  name_kh: string | null;
  date: string;
  is_paid: boolean;
  description: string | null;
  created_by: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  lifecycle: LifecycleDTO;
}

export interface PublicHolidayCreateDTO {
  name: string;
  name_kh?: string | null;
  date: string;
  is_paid?: boolean;
  description?: string | null;
}

export interface PublicHolidayUpdateDTO {
  name?: string;
  name_kh?: string | null;
  date?: string;
  is_paid?: boolean;
  description?: string | null;
}

export interface PublicHolidayImportDefaultsDTO {
  year: number;
}

export interface PublicHolidayImportResultDTO {
  year: number;
  imported_count: number;
  skipped_count: number;
  imported: PublicHolidayDTO[];
  skipped_dates: string[];
}

export interface PublicHolidayListParams {
  year?: number;
  include_deleted?: boolean;
  deleted_only?: boolean;
  signal?: AbortSignal;
}
