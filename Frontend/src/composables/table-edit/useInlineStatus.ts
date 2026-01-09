import { ref } from "vue";

export type InlineStatusSaveFn<V extends string> = (
  id: string,
  next: V
) => Promise<unknown>;

export type InlineStatusConfig<Row, V extends string> = {
  defaultStatus: V;

  /** Prevent edit for some rows (deleted, locked, etc.) */
  isLocked?: (row: Row) => boolean;

  /** How to read/write status on the row */
  getStatus?: (row: Row) => V | string | null | undefined;
  setStatus?: (row: Row, next: V) => void;

  /** How to read row id */
  getId?: (row: Row) => string | number;

  /** UI helpers (MUST accept string to match InlineStatusCell props) */
  tagType?: (v?: string | null) => any;
  label?: (v?: string | null) => string;
};

export function useInlineStatus<
  Row extends Record<string, any>,
  V extends string
>(persist: InlineStatusSaveFn<V>, config: InlineStatusConfig<Row, V>) {
  const getId = config.getId ?? ((row: any) => row.id);
  const getStatus =
    config.getStatus ??
    ((row: any) => row.status as V | string | null | undefined);
  const setStatus =
    config.setStatus ??
    ((row: any, next: V) => {
      row.status = next;
    });

  const editingStatusRowId = ref<string | null>(null);
  const statusDraft = ref<V>(config.defaultStatus);

  // immutably updated for reactivity
  const statusSaving = ref<Record<string, boolean>>({});

  // IMPORTANT: these accept string|null to match InlineStatusCell
  const statusTagType = (v?: string | null) =>
    config.tagType ? config.tagType(v) : "info";

  const formatStatusLabel = (v?: string | null) => {
    if (config.label) return config.label(v);
    const s = String(v ?? "").trim();
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : "—";
  };

  const startEditStatus = (row: Row) => {
    if (config.isLocked?.(row)) return;
    editingStatusRowId.value = String(getId(row));

    const current = getStatus(row);
    statusDraft.value =
      (String(current ?? config.defaultStatus) as V) ?? config.defaultStatus;
  };

  const cancelEditStatus = () => {
    editingStatusRowId.value = null;
  };

  const saveStatus = async (row: Row, nextRaw: unknown) => {
    const id = String(getId(row));
    const next = String(nextRaw ?? config.defaultStatus) as V;

    const prev = String(getStatus(row) ?? config.defaultStatus) as V;
    if (prev === next) return cancelEditStatus();

    statusSaving.value = { ...statusSaving.value, [id]: true };

    // optimistic update
    setStatus(row, next);

    try {
      await persist(id, next);
    } catch (err) {

      setStatus(row, prev);
      throw err;
    } finally {
      statusSaving.value = { ...statusSaving.value, [id]: false };
      cancelEditStatus();
    }
  };

  return {
    editingStatusRowId,
    statusDraft,
    statusSaving,
    statusTagType,
    formatStatusLabel,
    startEditStatus,
    cancelEditStatus,
    saveStatus,
  };
}
