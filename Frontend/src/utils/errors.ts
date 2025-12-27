import { isDev } from "./env";

type ReportMode = "log" | "crash-in-dev";

export function reportError(
  err: unknown,
  context?: string,
  mode: ReportMode = "log"
) {
  const error = err instanceof Error ? err : new Error(String(err));
  const message = context ? `[${context}] ${error.message}` : error.message;

  // Always log (dev + prod)
  console.error(message, error);

  // Only crash in dev when you explicitly want it
  if (isDev && mode === "crash-in-dev") {
    throw error;
  }

  return error;
}

// Programmer mistakes (invariants): crash in dev, log in prod
export function invariant(
  condition: unknown,
  message: string
): asserts condition {
  if (!condition) reportError(new Error(message), "invariant", "crash-in-dev");
}
