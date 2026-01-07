export type ISODateString = string;

export interface LifecycleDTO {
  /** ISO string */
  created_at: ISODateString;
  /** ISO string */
  updated_at: ISODateString;

  /**
   * Null (or undefined) means "active" (not deleted),
   * matches your Mongo queries: lifecycle.deleted_at == null
   */
  deleted_at: ISODateString | null;

  /** Who deleted it (null if not deleted) */
  deleted_by: string | null;
}
