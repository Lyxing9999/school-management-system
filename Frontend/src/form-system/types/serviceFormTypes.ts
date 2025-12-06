/* -------------------------------
 * Generic Form Service
 * ------------------------------- */
export interface UseFormService<
  TCreate = unknown,
  TUpdate = unknown,
  TDelete = boolean,
  TCreateResult = any,
  TUpdateResult = TCreateResult,
  TDetailResult = TCreateResult
> {
  create?: (data: TCreate) => Promise<TCreateResult>;
  update?: (id: string, data: TUpdate) => Promise<TUpdateResult>;
  delete?: (id: string) => Promise<TDelete>;
  getDetail?: (id: string) => Promise<TDetailResult>;
}
