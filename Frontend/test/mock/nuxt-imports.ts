// Re-export Vue's composition API
export {
  ref,
  reactive,
  computed,
  watch,
  watchEffect,
  onMounted,
  onUnmounted,
  onBeforeMount,
  onBeforeUnmount,
  onUpdated,
  onBeforeUpdate,
  defineComponent,
  defineAsyncComponent,
  nextTick,
  toRef,
  toRefs,
  unref,
  isRef,
} from "vue";

// Re-export from nuxt-app mock
export {
  useRouter,
  useRoute,
  useRuntimeConfig,
  navigateTo,
  abortNavigation,
  setPageLayout,
  definePageMeta,
} from "./nuxt-app";
