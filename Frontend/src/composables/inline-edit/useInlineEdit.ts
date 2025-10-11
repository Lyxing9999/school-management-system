import { ref } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { getKey } from "~/utils/aliasMapper";

export interface UseInlineEditService<T> {
  update: (id: string, payload: Partial<T>) => Promise<T>;
  delete: (id: string) => Promise<void>;
}

export function toInlineEditUpdateService<T>(
  service: UseFormDetailService<any, Partial<T>, T>
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

export function useInlineEdit<T extends { id: string | number }>(
  initialData: T[],
  service: UseInlineEditService<T>
) {
  const data = ref<T[]>([...initialData]);
  const rowLoading = ref<Record<string | number, boolean>>({});
  const originalRows = ref<Record<string | number, T>>({});
  const previousValues = ref<Record<string | number, Record<keyof T, any[]>>>(
    {}
  );
  const revertedFields = ref<Record<string | number, Set<keyof T>>>({});
  const save = async (
    row: T,
    field: string | number | symbol,
    autoSave = false
  ) => {
    const key = field as keyof T;
    const rowKey = getKey(row.id);
    const currentValue = row[key];
    const payload: Partial<T> = { [key]: currentValue } as Partial<T>;

    if (currentValue === "" || currentValue == null) {
      row[key] = originalRows.value[rowKey]?.[key] ?? currentValue;
      ElMessage.info("This field cannot be empty.");
      return;
    }

    rowLoading.value[rowKey] = true;

    try {
      const updated = await service.update(row.id.toString(), payload);

      if (!updated) {
        row[key] = originalRows.value[rowKey]?.[key] ?? currentValue;
        return;
      }

      const index = data.value.findIndex((r) => r.id === row.id);
      if (index !== -1)
        data.value[index] = { ...data.value[index], ...updated };
      revertedFields.value[rowKey] = revertedFields.value[rowKey] || new Set();

      if (autoSave && !revertedFields.value[rowKey].has(key)) {
        previousValues.value[rowKey] = previousValues.value[rowKey] || {};
        previousValues.value[rowKey][key] =
          previousValues.value[rowKey][key] || [];
        previousValues.value[rowKey][key].push(
          originalRows.value[rowKey]?.[key] ?? currentValue
        );
      }

      revertedFields.value[rowKey].delete(key);

      originalRows.value[rowKey] = { ...row } as T;
    } finally {
      rowLoading.value[rowKey] = false;
    }
  };
  const autoSave = async (row: T, field: string | number | symbol) => {
    const key = field as keyof T;
    const rowKey = getKey(row.id);
    const originalValue = originalRows.value[rowKey]?.[key];
    const currentValue = row[key];

    if (currentValue === originalValue) {
      return;
    }

    await save(row, key, true);
  };
  const cancel = (row: T) => {
    const rowKey = getKey(row.id);
    const original = originalRows.value[rowKey];
    if (original) Object.assign(row, original);
  };

  const remove = async (row: T) => {
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

      rowLoading.value[rowKey] = true;
      await service.delete(row.id.toString());

      data.value = data.value.filter((r) => r.id !== row.id);
      delete originalRows.value[rowKey];
      delete previousValues.value[rowKey];
    } catch (err) {
      if (err !== "cancel" && err !== "close")
        console.error("Failed to delete", err);
    } finally {
      rowLoading.value[rowKey] = false;
    }
  };

  const getPreviousValue = (row: T, field: keyof T) => {
    const rowKey = getKey(row.id);
    const stack = previousValues.value[rowKey]?.[field];
    return stack && stack.length ? stack[stack.length - 1] : "-";
  };

  const revertField = (row: T, field: keyof T) => {
    const rowKey = getKey(row.id);
    const stack = previousValues.value[rowKey]?.[field];
    if (stack && stack.length) {
      row[field] = stack.pop();
      revertedFields.value[rowKey] = revertedFields.value[rowKey] || new Set();
      revertedFields.value[rowKey].add(field);
    }
  };

  const setData = (newData: T[]) => {
    data.value = [...newData];
    newData.forEach((row) => {
      const rowKey = getKey(row.id);
      originalRows.value[rowKey] = { ...row };
      previousValues.value[rowKey] = {} as Record<keyof T, any[]>;
    });
  };

  return {
    data,
    rowLoading,
    save,
    cancel,
    remove,
    setData,
    autoSave,
    getPreviousValue,
    revertField,
  };
}
