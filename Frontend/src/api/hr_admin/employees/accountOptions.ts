import { displayRelation } from "~/api/hr_admin/shared/displayRelation";
import type { HrEmployeeAccountListItemDTO } from "./dto";

export type AccountSelectOption = {
  value: string;
  label: string;
};

export function normalizeAccountRole(raw?: string | null): string {
  return String(raw ?? "")
    .trim()
    .toLowerCase();
}

export function buildAccountOptionLabel(
  item: HrEmployeeAccountListItemDTO,
  fallbackLabel: string,
): string {
  const primary = displayRelation(
    item.account_name ?? item.username ?? item.email,
    item.user_id,
    fallbackLabel,
  );
  const secondary = String(item.account_email ?? item.email ?? "").trim();
  if (!secondary || secondary === primary) return primary;
  return `${primary} • ${secondary}`;
}

export function toAccountSelectOption(
  item: HrEmployeeAccountListItemDTO,
  fallbackLabel = "Account",
): AccountSelectOption | null {
  const userId = String(item.user_id ?? "").trim();
  if (!userId) return null;
  return {
    value: userId,
    label: buildAccountOptionLabel(item, fallbackLabel),
  };
}

export function toManagerSelectOptions(
  items: HrEmployeeAccountListItemDTO[],
): AccountSelectOption[] {
  return items
    .filter((item) => normalizeAccountRole(item.role) === "manager")
    .map((item) => toAccountSelectOption(item, "Manager"))
    .filter((item): item is AccountSelectOption => !!item);
}
