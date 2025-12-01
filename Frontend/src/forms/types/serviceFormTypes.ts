/* -------------------------------
 * Generic Form Service
 * ------------------------------- */
export interface UseFormService<
  TCreate,
  TUpdate,
  TDelete = boolean,
  TRetrieve = any
> {
  create?: (data: TCreate) => Promise<TRetrieve>;
  update: (id: string, data: TUpdate) => Promise<TRetrieve>;
  delete?: (id: string) => Promise<TDelete>;
  getDetail?: (id: string) => Promise<TRetrieve>;
}
