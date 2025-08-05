<script setup lang="ts">
import BaseSidebar from "~/components/layout/BaseSideBar.vue";
import schoolLogo from "~/assets/image/school_logo.png";
import { useRoute } from "vue-router";
const route = useRoute();

const sidebarClasses = {
  asideClass: "bg-[var(--color-light)] dark:bg-[var(--color-sidebar-dark)]",
  logoSectionClass:
    "p-4 mt-5 mx-auto flex items-center justify-center w-44 h-44 rounded-full  hover:cursor-pointer hover:scale-105 ",
  menuClass:
    "border-none text-[var(--menu-text-color)] dark:text-[var(--color-secondary-light)]",
  menuItemClass:
    "px-4 py-3 rounded-lg transition-colors duration-200 bg-[var(--color-sidebar-light)] dark:bg-[var(--color-sidebar-dark)] hover:bg-[var(--color-primary)] hover:text-[var(--color-light)] dark:hover:text-[var(--color-dark)]",
  menuIconClass: "text-xl leading-none text-[var(--color-primary)]",
  menuIconStyle: (item: { route: string }) => ({
    color:
      route.path === item.route
        ? "var(--color-primary)"
        : "var(--menu-text-color)",
  }),
  menuTitleClass:
    "ml-2 text-base font-semibold text-[var(--color-secondary-dark)] dark:text-[var(--color-secondary-light)]",
};
</script>

<template>
  <BaseSidebar
    :is-mobile="false"
    :logo-src="schoolLogo"
    :logo-section-class="sidebarClasses.logoSectionClass"
    :aside-class="sidebarClasses.asideClass"
    :menu-class="sidebarClasses.menuClass"
    :menu-icon-class="sidebarClasses.menuIconClass"
    :menu-icon-style="sidebarClasses.menuIconStyle"
    :menu-title-class="sidebarClasses.menuTitleClass"
  />
</template>
