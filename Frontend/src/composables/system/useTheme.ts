
type Theme = "light" | "dark";

export function useTheme() {
  const themeCookie = useCookie<Theme>("theme", {
    sameSite: "lax",
    path: "/",
  });

  function applyTheme(t: Theme) {
    const el = document.documentElement;
    el.setAttribute("data-theme", t);
    if (t === "dark") el.classList.add("dark");
    else el.classList.remove("dark");
  }

  function initFromClient() {
    if (import.meta.server) return;
    const stored = (localStorage.getItem("theme") as Theme | null) || null;
    const t: Theme = stored || themeCookie.value || "light";

    themeCookie.value = t;
    localStorage.setItem("theme", t);
    applyTheme(t);
  }

  function setTheme(t: Theme) {
    if (import.meta.client) {
      localStorage.setItem("theme", t);
      applyTheme(t);
    }
    themeCookie.value = t; // 
  }

  return { initFromClient, setTheme };
}
