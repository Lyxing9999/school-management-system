// composables/useTheme.ts
export type ThemeMode = "light" | "dark";
export const THEME_COOKIE = "theme";

export function useTheme() {
  // 1. Read Cookie (SSR & Client friendly)
  const themeCookie = useCookie<ThemeMode>(THEME_COOKIE, {
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 365, // Persist for 1 year
  });

  // 2. Global State Management
  const theme = useState<ThemeMode>(
    "theme-mode",
    () => themeCookie.value ?? "light"
  );

  // 3. Computed Helper
  const isDark = computed(() => theme.value === "dark");

  // 4. Synchronization Function
  function setTheme(mode: ThemeMode) {
    theme.value = mode;
    themeCookie.value = mode; // Updates cookie automatically
  }

  function toggle() {
    setTheme(isDark.value ? "light" : "dark");
  }

  /**
   * 5. Declarative Head Management (The Architect's Choice)
   * This automatically injects class="dark" or class="light" into the <html> tag.
   * works on Server AND Client.
   */
  useHead({
    htmlAttrs: {
      class: () => theme.value,
      "data-theme": () => theme.value,
    },
    meta: [{ name: "color-scheme", content: () => theme.value }],
  });

  /**
   * 6. System Preference Detection (Client Only)
   * Only runs if no cookie exists.
   */
  function initSystemPreference() {
    if (!process.client) return;

    // If cookie exists, Nuxt already handled the state via useState/useCookie
    if (themeCookie.value) return;

    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;
    setTheme(prefersDark ? "dark" : "light");
  }

  return {
    theme,
    isDark,
    setTheme,
    toggle,
    initSystemPreference,
  };
}
