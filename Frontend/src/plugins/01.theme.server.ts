
export default defineNuxtPlugin(() => {

  const themeCookie = useCookie<"light" | "dark">("theme", {
    sameSite: "lax",
    path: "/",
  });

  const theme = themeCookie.value || "light";


  useHead({
    htmlAttrs: {
      "data-theme": theme,
      class: theme === "dark" ? "dark" : undefined,
    },
  });
});
