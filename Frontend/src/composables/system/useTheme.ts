import { computed } from "vue";

export type ThemeKey = "light" | "dark";

const STORAGE_KEY = "theme";

function isTheme(v: unknown): v is ThemeKey {
  return v === "light" || v === "dark";
}

export function useTheme() {
  // Keeps state across app; SSR default is stable.
  const theme = useState<ThemeKey>("theme", () => "light");
  const isDark = computed(() => theme.value === "dark");

  function apply(next: ThemeKey) {
    theme.value = next;

    if (!import.meta.client) return;

    const el = document.documentElement;
    el.setAttribute("data-theme", next);
    el.classList.toggle("dark", next === "dark");
    localStorage.setItem(STORAGE_KEY, next);
  }

  function initFromClient() {
    if (!import.meta.client) return;

    const saved = localStorage.getItem(STORAGE_KEY);
    if (isTheme(saved)) {
      apply(saved);
      return;
    }

    const attr = document.documentElement.getAttribute("data-theme");
    if (isTheme(attr)) {
      apply(attr);
      return;
    }

    apply("light");
  }

  function toggle() {
    apply(isDark.value ? "light" : "dark");
  }

  return { theme, isDark, apply, toggle, initFromClient };
}
