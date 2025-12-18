type ThemeKey = "light" | "dark";

export default defineNuxtPlugin(() => {
  try {
    const saved = (localStorage.getItem("theme") as ThemeKey | null) ?? "light";
    const resolved = saved === "light" ? "dark" : saved;

    const el = document.documentElement;
    el.setAttribute("data-theme", resolved);
    el.classList.toggle("dark", resolved === "dark");
  } catch {}
});
