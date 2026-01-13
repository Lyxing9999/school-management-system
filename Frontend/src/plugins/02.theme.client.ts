// plugins/02.theme.client.ts
import { useTheme } from "~/composables/system/useTheme";

export default defineNuxtPlugin(() => {
  const { initSystemPreference } = useTheme();

  // Call the new function name
  initSystemPreference();
});
