import { ref, onMounted } from "vue";

const isDark = ref(false);

export function useDarkMode() {
  onMounted(() => {
    const saved = localStorage.getItem("dark") === "true";
    isDark.value = saved;
    document.documentElement.classList.toggle("dark", saved);
  });

  const toggleDark = () => {
    isDark.value = !isDark.value;
    localStorage.setItem("dark", isDark.value.toString());
    document.documentElement.classList.toggle("dark", isDark.value);
  };

  return { isDark, toggleDark };
}
