export type LifecycleDTO = {
  created_at: string;
  updated_at?: string | null;
  deleted_at?: string | null;
  deleted_by?: string | null;
};

export type WorkLocationDTO = {
  id: string;
  name: string;
  location_name?: string | null;
  address: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
  is_active: boolean;
  created_by?: string | null;
  created_by_name?: string | null;
  deleted_by?: string | null;
  deleted_by_name?: string | null;
  lifecycle: LifecycleDTO;
};

export type WorkLocationCreateDTO = {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
  is_active?: boolean;
};

export type WorkLocationUpdateDTO = Partial<{
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  radius_meters: number;
  is_active: boolean;
}>;

export type WorkLocationListParams = Partial<{
  q: string;
  status: "active" | "inactive" | "deleted" | "all";
}>;
