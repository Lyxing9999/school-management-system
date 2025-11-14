// Generic paginated response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}

// Generic action response
export interface ActionResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
}

// -------------------------
// List / Pagination service
// -------------------------
export interface UseListService<P = any, F = any, L = P> {
  page?: (filter: F) => Promise<PaginatedResponse<P>>;
  all?: () => Promise<L[]>;
}

// -------------------------
// Search service
// -------------------------
export interface UseSearchService<P = any, S = any> {
  search?: (query: S) => Promise<P[]>;
}

// -------------------------
// Assign / Modify service
// -------------------------
export interface UseModifyService<
  TAssign,
  TUnassign = TAssign,
  TResponse = any
> {
  assign?: (id: string, data: TAssign) => Promise<ActionResponse<TResponse>>;
  unassign?: (
    id: string,
    data?: TUnassign
  ) => Promise<ActionResponse<TResponse>>;
  customAction?: (id: string, data?: any) => Promise<ActionResponse<TResponse>>;
}
