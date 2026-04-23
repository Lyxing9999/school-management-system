export function displayRelation(
  name?: string | null,
  fallbackId?: string | null,
  fallback = "-",
): string {
  const normalizedName = String(name ?? "").trim();
  if (normalizedName) return normalizedName;

  const normalizedId = String(fallbackId ?? "").trim();
  if (normalizedId) return normalizedId;

  return fallback;
}
