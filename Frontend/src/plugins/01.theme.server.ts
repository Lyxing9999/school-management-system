import { useTheme } from "~/composables/system/useTheme";

export default defineNuxtPlugin(() => {
  const themeCookie = useCookie<"light" | "dark">("theme", {
    sameSite: "lax",
    path: "/",
  });

  const theme = themeCookie.value || "light";

  useHead({
    htmlAttrs: {
      class: theme === "dark" ? "dark" : "light",
      "data-theme": theme,
      style: `color-scheme: ${theme};`,
    },
  });
});
