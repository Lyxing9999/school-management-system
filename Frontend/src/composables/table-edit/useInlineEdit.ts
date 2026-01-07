import { ref } from "vue";
import type { AxiosError } from "axios";
import { ElMessageBox, ElMessage } from "element-plus";
import { getKey } from "~/utils/alias/aliasMapper";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";

export interface UseInlineEditService<TUpdate, TReturn = any> {
  update: (id: string, payload: Partial<TUpdate>) => Promise<TReturn>;
  delete: (id: string) => Promise<void>;
}

export function toInlineEditUpdateService<TUpdate, TReturn = any>(
  service: () => UseFormService<any, Partial<TUpdate>, any, TReturn>
): UseInlineEditService<TUpdate, TReturn> {
  return {
    update: async (id: string, payload: Partial<TUpdate>) => {
      const s = service();
      if (!s.update) throw new Error("Update method not implemented");
      return await s.update(id, payload);
    },
    delete: async (id: string) => {
      const s = service();
      if (!s.delete) throw new Error("Delete method not implemented");
      return await s.delete(id);
    },
  };
}

type ApiErr = { status?: number; message: string };

function parseApiError(err: unknown): ApiErr {
  const e = err as AxiosError<any>;
  const status = e?.response?.status;
  const message =
    e?.response?.data?.message ||
    e?.response?.data?.error ||
    e?.message ||
    "Update failed.";
  return { status, message };
}

function isValidationLike(status?: number) {
  return status === 400 || status === 409 || status === 422;
}

function shallowClone<T extends object>(v: T): T {
  return { ...(v as any) };
}

export function useInlineEdit<
  TGet extends { id: string | number },
  TUpdate extends object,
  TReturn = Partial<TGet> | TGet
>(
  initialData: TGet[] = [],
  inlineEditService: { value: UseInlineEditService<TUpdate, TReturn> }
) {
  const service = inlineEditService.value;

  const data = ref<TGet[]>([]);

  /** `${id}:${field}` -> boolean */
  const inlineEditLoading = ref<Record<string, boolean>>({});
  const deleteLoading = ref<Record<string | number, boolean>>({});

  /**
   * rowKey -> latest server-truth snapshot (updates after each success save)
   */
  const originalRows = ref<Record<string | number, TGet>>({});

  /**
   * rowKey -> FIRST server-truth snapshot (never changes until setData)
   * This is your "main original value"
   */
  const baseOriginalRows = ref<Record<string | number, TGet>>({});

  /**
   * rowKey -> fieldKey(string) -> stack of previous saved values (UNDO stack)
   * We PUSH on every successful save when value changes.
   * We POP on revert so it steps back.
   */
  const previousValues = ref<Record<string | number, Record<string, any[]>>>(
    {}
  );

  /** `${id}:${field}` -> error message */
  const fieldErrors = ref<Record<string, string>>({});

  const fieldToGetKey = (field: keyof TUpdate): keyof TGet =>
    field as unknown as keyof TGet;

  const cellKey = (id: string | number, field: PropertyKey) =>
    `${String(id)}:${String(field)}`;

  const isCellSaving = (row: TGet, field: keyof TUpdate) =>
    inlineEditLoading.value[cellKey(row.id, field)] ?? false;

  const isRowSaving = (row: TGet) => {
    const prefix = `${String(row.id)}:`;
    return Object.entries(inlineEditLoading.value).some(
      ([k, v]) => v && k.startsWith(prefix)
    );
  };

  function setFieldError(row: TGet, field: keyof TUpdate, message: string) {
    fieldErrors.value = {
      ...fieldErrors.value,
      [cellKey(row.id, field)]: message,
    };
  }

  function clearFieldError(row: TGet, field: keyof TUpdate) {
    const ck = cellKey(row.id, field);
    if (!fieldErrors.value[ck]) return;
    const next = { ...fieldErrors.value };
    delete next[ck];
    fieldErrors.value = next;
  }

  function getFieldError(row: TGet, field: keyof TUpdate): string | null {
    return fieldErrors.value[cellKey(row.id, field)] ?? null;
  }

  function pushHistory(rowKey: string | number, fieldKey: string, prev: any) {
    previousValues.value[rowKey] = previousValues.value[rowKey] || {};
    previousValues.value[rowKey][fieldKey] =
      previousValues.value[rowKey][fieldKey] || [];
    previousValues.value[rowKey][fieldKey].push(prev);
  }

  /**
   * Can revert if:
   * - undo stack has something OR
   * - current UI value differs from *base original* (main original)
   *
   * This makes "revert" possible even when user typed and never saved:
   * it will revert to baseOriginal (main original).
   */
  const canRevert = (row: TGet, field: keyof TUpdate) => {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);
    const keyStr = String(key);

    const stack = previousValues.value[rowKey]?.[keyStr];
    if (stack && stack.length) return true;

    const mainOriginal = baseOriginalRows.value[rowKey]?.[key];
    const current = (row as any)[key];
    return mainOriginal !== undefined && current !== mainOriginal;
  };

  /**
   * Tooltip:
   * - if stack has value => show the value you will revert to (top)
   * - else => show base original (main original)
   */
  const getPreviousValue = (row: TGet, field: keyof TUpdate) => {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);
    const keyStr = String(key);

    const stack = previousValues.value[rowKey]?.[keyStr];
    if (stack && stack.length) return String(stack[stack.length - 1]);

    const mainOriginal = baseOriginalRows.value[rowKey]?.[key];
    return mainOriginal !== undefined ? String(mainOriginal) : "-";
  };

  /**
   * Revert:
   * - if stack has values => POP and set that value (step-back)
   * - else => revert to base original (main original)
   * Clears error afterward.
   */
  const revertField = (row: TGet, field: keyof TUpdate) => {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);
    const keyStr = String(key);

    const stack = previousValues.value[rowKey]?.[keyStr];

    if (stack && stack.length) {
      (row as any)[key] = stack.pop();
    } else {
      const mainOriginal = baseOriginalRows.value[rowKey]?.[key];
      if (mainOriginal !== undefined) (row as any)[key] = mainOriginal;
    }

    clearFieldError(row, field);
  };

  /**
   * Force revert to "real server snapshot" (latest saved snapshot).
   * Used on ANY error.
   */
  function revertToLatestServerTruth(row: TGet, field: keyof TUpdate) {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);
    const prevSaved = originalRows.value[rowKey]?.[key];
    if (prevSaved !== undefined) (row as any)[key] = prevSaved;
  }

  /**
   * Save:
   * - Success:
   *   - pushHistory(prevSaved) if changed (UNDO stack)
   *   - force saved field into patch
   *   - update row + data[] + originalRows snapshot
   *   - clear error
   * - Error (ANY error including 400/409/422):
   *   - revert UI to latest server snapshot (originalRows)
   *   - set error
   */
  const save = async (row: TGet, field: keyof TUpdate, autoSave = false) => {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);
    const keyStr = String(key);

    if (isCellSaving(row, field)) return;

    const nextValue = (row as any)[key];
    const prevSaved = originalRows.value[rowKey]?.[key];

    // empty validation -> error + revert to latest server snapshot
    if (nextValue === "" || nextValue == null) {
      revertToLatestServerTruth(row, field);
      setFieldError(row, field, "This field cannot be empty.");
      if (!autoSave) ElMessage.info("This field cannot be empty.");
      return;
    }

    const ck = cellKey(row.id, field);
    inlineEditLoading.value = { ...inlineEditLoading.value, [ck]: true };
    clearFieldError(row, field);

    try {
      const payload: Partial<TUpdate> = { [field]: nextValue } as any;
      const updated = await service.update(String(row.id), payload);

      if (!updated) {
        revertToLatestServerTruth(row, field);
        setFieldError(row, field, "Failed to update.");
      }

      // PUSH previous saved value for UNDO stack (every success if changed)
      if (prevSaved !== undefined && prevSaved !== nextValue) {
        pushHistory(rowKey, keyStr, prevSaved);
      }

      // backend may return partial patch: force saved field into patch
      const patch = {
        ...(updated as unknown as Partial<TGet>),
        [key]: nextValue,
      } as Partial<TGet>;

      Object.assign(row, patch);

      const index = data.value.findIndex((r) => r.id === row.id);
      if (index !== -1) {
        data.value[index] = { ...data.value[index], ...patch };
        originalRows.value[rowKey] = shallowClone(data.value[index]) as TGet;
      } else {
        originalRows.value[rowKey] = shallowClone(row) as TGet;
      }

      clearFieldError(row, field);
    } catch (err) {
      const { status, message } = parseApiError(err);

      revertToLatestServerTruth(row, field);
      setFieldError(row, field, message);

      if (!autoSave) {
        if (isValidationLike(status)) ElMessage.warning(message);
        else ElMessage.error(message);
      }
    } finally {
      inlineEditLoading.value = { ...inlineEditLoading.value, [ck]: false };
    }
  };

  const autoSave = async (row: TGet, field: keyof TUpdate) => {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);

    const originalValue = originalRows.value[rowKey]?.[key];
    const currentValue = (row as any)[key];

    if (currentValue === originalValue) return;
    await save(row, field, true);
  };

  const cancel = (row: TGet) => {
    const rowKey = getKey(row.id);
    const original = originalRows.value[rowKey];
    if (original) Object.assign(row, original);

    // clear errors for this row
    const prefix = `${String(row.id)}:`;
    const nextErr = { ...fieldErrors.value };
    Object.keys(nextErr).forEach((k) => {
      if (k.startsWith(prefix)) delete nextErr[k];
    });
    fieldErrors.value = nextErr;
  };

  const remove = async (row: TGet) => {
    const rowKey = getKey(row.id);

    try {
      await ElMessageBox.confirm(
        "Are you sure you want to delete this row?",
        "Warning",
        { confirmButtonText: "Yes", cancelButtonText: "No", type: "warning" }
      );
    } catch {
      return;
    }

    try {
      deleteLoading.value = { ...deleteLoading.value, [rowKey]: true };
      await service.delete(String(row.id));

      data.value = data.value.filter((r) => r.id !== row.id);

      delete originalRows.value[rowKey];
      delete baseOriginalRows.value[rowKey];
      delete previousValues.value[rowKey];

      // clear errors
      const prefix = `${String(row.id)}:`;
      const nextErr = { ...fieldErrors.value };
      Object.keys(nextErr).forEach((k) => {
        if (k.startsWith(prefix)) delete nextErr[k];
      });
      fieldErrors.value = nextErr;
    } finally {
      deleteLoading.value = { ...deleteLoading.value, [rowKey]: false };
    }
  };

  const setData = (newData: TGet[]) => {
    data.value = [...newData];

    const nextOriginal: Record<string | number, TGet> = {};
    const nextBase: Record<string | number, TGet> = {};
    const nextPrev: Record<string | number, Record<string, any[]>> = {};

    newData.forEach((row) => {
      const rowKey = getKey(row.id);
      const snap = shallowClone(row) as TGet;

      nextOriginal[rowKey] = snap;
      nextBase[rowKey] = shallowClone(row) as TGet; // main original (never changes)
      nextPrev[rowKey] = {};
    });

    originalRows.value = nextOriginal;
    baseOriginalRows.value = nextBase;
    previousValues.value = nextPrev;
    fieldErrors.value = {};
  };

  // init
  setData(initialData);

  return {
    data,
    inlineEditLoading,
    deleteLoading,

    save,
    autoSave,
    cancel,
    remove,
    setData,

    // revert + tooltip
    canRevert,
    revertField,
    getPreviousValue,

    // helpers
    cellKey,
    isCellSaving,
    isRowSaving,

    // error UI
    fieldErrors,
    getFieldError,
  };
}
