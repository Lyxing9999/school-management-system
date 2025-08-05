<script lang="ts" setup>
import BaseSidebar from "~/components/layout/BaseSideBar.vue";
import { useRoute } from "vue-router";
import schoolLogo from "~/assets/image/school_logo.png";

const route = useRoute();

const sidebarClasses = {
  asideClass: "bg-[var(--color-light)] dark:bg-[var(--color-sidebar-dark)]",
};
</script>
<template>
  <BaseSidebar
    :is-mobile="false"
    :aside-class="sidebarClasses.asideClass"
    :logo-src="schoolLogo"
  />
</template>
