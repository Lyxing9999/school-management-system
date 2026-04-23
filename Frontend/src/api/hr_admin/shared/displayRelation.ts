const MONGO_OBJECT_ID_REGEX = /^[a-f0-9]{24}$/i;

export function displayRelation(
  name?: string | null,
  fallbackId?: string | null,
  fallback = "-",
): string {
  const normalizedName = String(name ?? "").trim();
  if (normalizedName) return normalizedName;

  const normalizedId = String(fallbackId ?? "").trim();
  if (!normalizedId) return fallback;
  if (MONGO_OBJECT_ID_REGEX.test(normalizedId)) return fallback;
  return normalizedId;
}
