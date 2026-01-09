import { useTheme } from "~/composables/system/useTheme";

export default defineNuxtPlugin(() => {
  const { initFromClient } = useTheme();
  initFromClient();
});
