import { computed } from "vue";

type ThemeMode = "light" | "dark";
const THEME_COOKIE = "theme";

export function useTheme() {
  // cookie is readable on server + client in Nuxt
  const themeCookie = useCookie<ThemeMode>(THEME_COOKIE, {
    sameSite: "lax",
    path: "/",
    // optionally: maxAge: 60 * 60 * 24 * 365,
  });

  // state so all components reactively update
  const theme = useState<ThemeMode>(
    "theme-mode",
    () => themeCookie.value ?? "light"
  );

  const isDark = computed(() => theme.value === "dark");

  function applyToDom(mode: ThemeMode) {
    if (!process.client) return;
    const root = document.documentElement;
    root.classList.toggle("dark", mode === "dark");
    root.classList.toggle("light", mode === "light");
    root.dataset.theme = mode;

    // helps built-in form controls match theme in some browsers
    root.style.colorScheme = mode;
  }

  function setTheme(mode: ThemeMode) {
    theme.value = mode;
    themeCookie.value = mode;
    applyToDom(mode);
  }

  function toggle() {
    setTheme(isDark.value ? "light" : "dark");
  }

  /**
   * Client-only initializer:
   * - if no cookie yet, use system preference once
   * - always apply to DOM
   */
  function initFromClient() {
    if (!process.client) return;

    // If cookie not set, take system preference initially
    if (!themeCookie.value) {
      const prefersDark =
        window.matchMedia?.("(prefers-color-scheme: dark)")?.matches ?? false;
      setTheme(prefersDark ? "dark" : "light");
      return;
    }

    // Ensure DOM matches current state/cookie
    theme.value = themeCookie.value;
    applyToDom(theme.value);
  }

  return { theme, isDark, setTheme, toggle, initFromClient };
}
