import type { ColumnConfig } from "~/components/types/tableEdit";
import type { InlineEditMode } from "~/stores/preferencesStore";

export function applyInlineEditMode<T extends Record<string, any>>(
  columns: ColumnConfig<T>[],
  mode: InlineEditMode
): ColumnConfig<T>[] {
  const isManual = mode === "manual";

  return columns.map((col) => {
    const isEditable = Boolean(col.component) && !col.operation && !col.useSlot;

    if (!isEditable) return col;

    return {
      ...col,
      autoSave: !isManual, // manual => false
      controls: isManual, // manual => true
      revertSlots: !isManual, // manual => true (same as your working version)
    };
  });
}
