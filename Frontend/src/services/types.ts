export interface PaginatedResponse<T> {
  items: T[];
  total: number;
}
export interface ActionResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
}
export interface UseFormService<
  C, // Create type
  U, // Update type
  D = boolean, // Delete return type
  R = any, // Detail type
  P = any, // Paginated list type
  F = any, // Filter type
  L = P // Full list type, default same as P
> {
  create?: (data: C) => Promise<any>;
  update: (id: string, data: U) => Promise<any>;
  delete?: (id: string) => Promise<D>;
  getDetail?: (id: string) => Promise<R>;
  // paginated list
  page?: (filter: F) => Promise<PaginatedResponse<P>>;
  all?: () => Promise<L[]>;
}

// -------------------------
// UseModifyService generic interface
// -------------------------
// TAssign = payload type for assign action
// TUnassign = payload type for unassign/remove action
// TResponse = returned DTO type
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
