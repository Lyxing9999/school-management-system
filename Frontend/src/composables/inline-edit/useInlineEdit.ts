import { ref, computed, type ComputedRef } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { getKey } from "~/utils/aliasMapper";
import type { UseFormService } from "~/services/types";

export interface UseInlineEditService<T> {
  update: (id: string, payload: Partial<T>) => Promise<T>;
  delete: (id: string) => Promise<void>;
}

export function toInlineEditUpdateService<T>(
  service: UseFormService<any, Partial<T>, any, Record<string, any>, any, any>
): UseInlineEditService<T> {
  return {
    update: async (id: string, payload: Partial<T>) => {
      if (!service.update) throw new Error("Update method not implemented");
      return await service.update(id, payload);
    },
    delete: async (id: string) => {
      if (!service.delete) throw new Error("Delete method not implemented");
      return await service.delete(id);
    },
  };
}

export function useInlineEdit<
  TGet extends { id: string | number },
  TUpdate extends object
>(
  initialData: TGet[] = [],
  inlineEditService: ComputedRef<UseInlineEditService<TUpdate>>
) {
  const service = inlineEditService.value;

  const data = ref<TGet[]>([...initialData]);
  const loading = ref<Record<string | number, boolean>>({});
  const originalRows = ref<Record<string | number, TGet>>({});
  const previousValues = ref<
    Record<string | number, Partial<Record<keyof TGet, any[]>>>
  >({});
  const revertedFields = ref<Record<string | number, Set<keyof TGet>>>({});

  // Helper to cast safely
  const fieldToGetKey = (field: keyof TUpdate): keyof TGet =>
    field as unknown as keyof TGet;

  const save = async (row: TGet, field: keyof TUpdate, autoSave = false) => {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);
    const currentValue = row[key] as any;

    // Validate
    if (currentValue === "" || currentValue == null) {
      row[key] = originalRows.value[rowKey]?.[key] ?? currentValue;
      ElMessage.info("This field cannot be empty.");
      return;
    }

    loading.value[rowKey] = true;

    try {
      // Store previous value if autoSave
      if (autoSave) {
        previousValues.value[rowKey] = previousValues.value[rowKey] || {};
        previousValues.value[rowKey][key] =
          previousValues.value[rowKey][key] || [];
        previousValues.value[rowKey][key].push(
          originalRows.value[rowKey]?.[key] ?? currentValue
        );
      }

      // Update payload
      const payload: Partial<TUpdate> = {
        [field]: currentValue,
      } as Partial<TUpdate>;
      const updated = await service.update(row.id.toString(), payload);

      if (!updated) {
        row[key] = originalRows.value[rowKey]?.[key] ?? currentValue;
        return;
      }

      // Merge updated values
      const index = data.value.findIndex((r) => r.id === row.id);
      if (index !== -1)
        data.value[index] = { ...data.value[index], ...updated };

      revertedFields.value[rowKey] = revertedFields.value[rowKey] || new Set();
      revertedFields.value[rowKey].delete(key);
      originalRows.value[rowKey] = { ...row };
    } finally {
      loading.value[rowKey] = false;
    }
  };

  const autoSave = async (row: TGet, field: keyof TUpdate) => {
    const rowKey = getKey(row.id);
    const key = fieldToGetKey(field);
    const originalValue = originalRows.value[rowKey]?.[key];
    const currentValue = row[key];
    if (currentValue === originalValue) return;
    await save(row, field, true);
  };

  const cancel = (row: TGet) => {
    const rowKey = getKey(row.id);
    const original = originalRows.value[rowKey];
    if (original) Object.assign(row, original);
  };

  const remove = async (row: TGet) => {
    const rowKey = getKey(row.id);
    try {
      await ElMessageBox.confirm(
        "Are you sure you want to delete this row?",
        "Warning",
        {
          confirmButtonText: "Yes",
          cancelButtonText: "No",
          type: "warning",
        }
      );
      loading.value[rowKey] = true;
      await service.delete(row.id.toString());
      data.value = data.value.filter((r) => r.id !== row.id);
      delete originalRows.value[rowKey];
      delete previousValues.value[rowKey];
    } finally {
      loading.value[rowKey] = false;
    }
  };

  const getPreviousValue = (row: TGet, field: keyof TGet) => {
    const rowKey = getKey(row.id);
    const stack = previousValues.value[rowKey]?.[field];
    return stack && stack.length ? stack[stack.length - 1] : "-";
  };

  const revertField = (row: TGet, field: keyof TGet) => {
    const rowKey = getKey(row.id);
    const stack = previousValues.value[rowKey]?.[field];
    if (stack && stack.length) {
      row[field] = stack.pop();
      revertedFields.value[rowKey] = revertedFields.value[rowKey] || new Set();
      revertedFields.value[rowKey].add(field);
    }
  };

  const setData = (newData: TGet[]) => {
    data.value = [...newData];
    newData.forEach((row) => {
      const rowKey = getKey(row.id);
      originalRows.value[rowKey] = { ...row };
      previousValues.value[rowKey] = {} as Record<keyof TGet, any[]>;
      Object.keys(row).forEach((field) => {
        previousValues.value[rowKey][field as keyof TGet] = [
          (row as any)[field],
        ];
      });
    });
  };

  return {
    data,
    loading,
    save,
    cancel,
    remove,
    setData,
    autoSave,
    getPreviousValue,
    revertField,
  };
}
