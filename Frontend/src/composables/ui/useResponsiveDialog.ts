import { ref, computed, onMounted, onBeforeUnmount, type Ref } from "vue";

type DialogSizePreset = {
  desktopMaxPx: number; // hard upper bound
  desktopMinPx: number; // hard lower bound
  desktopVw: number; // preferred vw
};

export function useResponsiveDialog(options?: {
  mobileBp?: number; // default 768
  preset?: DialogSizePreset;
}) {
  const mobileBp = options?.mobileBp ?? 768;

  const preset = options?.preset ?? {
    desktopMinPx: 520,
    desktopVw: 70,
    desktopMaxPx: 980,
  };

  const w = ref(1200);

  function sync() {
    if (process.server) return;
    w.value = window.innerWidth;
  }

  onMounted(() => {
    sync();
    window.addEventListener("resize", sync, { passive: true });
  });

  onBeforeUnmount(() => {
    if (process.server) return;
    window.removeEventListener("resize", sync);
  });

  const isMobile = computed(() => w.value <= mobileBp);

  /** Element Plus dialog width */
  const width = computed(() => {
    if (isMobile.value) return "100%";
    // clamp(min, preferred, max) — best “senior” default
    return `clamp(${preset.desktopMinPx}px, ${preset.desktopVw}vw, ${preset.desktopMaxPx}px)`;
  });

  /** Use fullscreen mode on mobile for best UX */
  const fullscreen = computed(() => isMobile.value);

  /** Top alignment: mobile should be flush; desktop can be lower */
  const top = computed(() => (isMobile.value ? "0" : "10vh"));

  return { isMobile, width, fullscreen, top };
}
