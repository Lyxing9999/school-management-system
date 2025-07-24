import { ref, onMounted, onBeforeUnmount } from "vue";

export function useWindowSize() {
  const width = ref(typeof window !== "undefined" ? window.innerWidth : 1200);

  const onResize = () => {
    width.value = window.innerWidth;
  };

  onMounted(() => window.addEventListener("resize", onResize));
  onBeforeUnmount(() => window.removeEventListener("resize", onResize));

  return { width };
}
