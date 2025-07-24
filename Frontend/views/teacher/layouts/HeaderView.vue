<script lang="ts" setup>
import BaseHeader from "~/components/Base/BaseHeader.vue";
import { ref } from "vue";
import { useAuthStore } from "~/stores/authStore";

const authStore = useAuthStore();
const user = authStore.user;

const title = ref("Teacher");
</script>

<template>
  <BaseHeader :user-name="user?.username" :title="title" />
</template>
