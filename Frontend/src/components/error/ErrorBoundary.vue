<!-- components/ErrorBoundary.vue -->
<script setup lang="ts">
import { ref, onErrorCaptured, defineProps, defineEmits } from "vue";

const props = defineProps<{
  onError?: (err: Error) => void; // optional custom handler
}>();

const emit = defineEmits<{
  (e: "reset"): void;
}>();

const error = ref<Error | null>(null);

function resetError() {
  error.value = null;
  emit("reset");
}

onErrorCaptured((err, instance, info) => {
  error.value = err as Error;
  console.error("ErrorBoundary captured:", err, info);
  props.onError?.(err as Error);
  return false; // stop propagation
});

defineSlots<{
  default(props: { error: Error | null; reset: () => void }): any;
  fallback(props: { error: Error; reset: () => void }): any;
}>();
</script>

<template>
  <div>
    <slot v-if="!error" :error="error" :reset="resetError"></slot>

    <slot name="fallback" v-else :error="error" :reset="resetError">
      <el-card
        class="p-6 w-full max-w-md mx-auto mt-6 border-red-300 bg-red-50"
      >
        <div class="flex flex-col items-center space-y-4">
          <el-icon color="red" size="36">
            <Warning />
          </el-icon>
          <h3 class="text-red-700 text-lg font-semibold text-center">
            Oops! Something went wrong.
          </h3>
          <p class="text-red-500 text-sm text-center break-words">
            {{ error.message }}
          </p>
          <el-button type="danger" @click="resetError">Retry</el-button>
        </div>
      </el-card>
    </slot>
  </div>
</template>
