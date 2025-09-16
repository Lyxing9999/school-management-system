import { ref } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";

export function useInlineEdit<T extends { id: string | number }>(
  initialData: T[],
  service: {
    update: (id: string | number, payload: Partial<T>) => Promise<T | null>;
    remove: (id: string | number) => Promise<void>;
  }
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
    const currentValue = row[key];
    const payload: Partial<T> = { [key]: currentValue } as Partial<T>;

    if (currentValue === "" || currentValue == null) {
      row[key] = originalRows.value[row.id]?.[key] ?? currentValue;
      ElMessage.info("This field cannot be empty.");
      return;
    }

    rowLoading.value[row.id] = true;

    try {
      const updated = await service.update(row.id, payload);

      if (!updated) {
        row[key] = originalRows.value[row.id]?.[key] ?? currentValue;
        return;
      }

      const index = data.value.findIndex((r) => r.id === row.id);
      if (index !== -1)
        data.value[index] = { ...data.value[index], ...updated };
      revertedFields.value[row.id] = revertedFields.value[row.id] || new Set();

      if (autoSave && !revertedFields.value[row.id].has(key)) {
        previousValues.value[row.id] = previousValues.value[row.id] || {};
        previousValues.value[row.id][key] =
          previousValues.value[row.id][key] || [];
        previousValues.value[row.id][key].push(
          originalRows.value[row.id]?.[key] ?? currentValue
        );
      }

      revertedFields.value[row.id].delete(key);

      originalRows.value[row.id] = { ...row } as T;
    } finally {
      rowLoading.value[row.id] = false;
    }
  };
  const autoSave = async (row: T, field: string | number | symbol) => {
    const key = field as keyof T;
    const originalValue = originalRows.value[row.id]?.[key];
    const currentValue = row[key];

    if (currentValue === originalValue) {
      return;
    }

    await save(row, key, true);
  };
  const cancel = (row: T) => {
    const original = originalRows.value[row.id];
    if (original) Object.assign(row, original);
  };

  const remove = async (row: T) => {
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

      rowLoading.value[row.id] = true;
      await service.remove(row.id);

      data.value = data.value.filter((r) => r.id !== row.id);
      delete originalRows.value[row.id];
      delete previousValues.value[row.id];
    } catch (err) {
      if (err !== "cancel" && err !== "close")
        console.error("Failed to delete", err);
    } finally {
      rowLoading.value[row.id] = false;
    }
  };

  const getPreviousValue = (row: T, field: keyof T) => {
    const stack = previousValues.value[row.id]?.[field];
    return stack && stack.length ? stack[stack.length - 1] : "-";
  };

  const revertField = (row: T, field: keyof T) => {
    const stack = previousValues.value[row.id]?.[field];
    if (stack && stack.length) {
      row[field] = stack.pop();
      revertedFields.value[row.id] = revertedFields.value[row.id] || new Set();
      revertedFields.value[row.id].add(field);
    }
  };

  const setData = (newData: T[]) => {
    data.value = [...newData];
    newData.forEach((row) => {
      originalRows.value[row.id] = { ...row };
      previousValues.value[row.id] = {} as Record<keyof T, any[]>;
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
