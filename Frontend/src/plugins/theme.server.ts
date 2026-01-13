import { useTheme } from "~/composables/system/useTheme";

export default defineNuxtPlugin(() => {
  const { theme, isDark } = useTheme();

  // Important: set SSR html attributes based on cookie/state
  useHead({
    htmlAttrs: {
      class: isDark.value ? "dark" : "light",
      "data-theme": theme.value,
      style: `color-scheme: ${theme.value};`,
    },
  });
});
