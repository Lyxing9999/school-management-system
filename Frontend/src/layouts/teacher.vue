<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import TeacherHeader from "~/views/teacher/layouts/HeaderView.vue";
import TeacherFooter from "~/views/teacher/layouts/FooterView.vue";
import TeacherSidebar from "~/views/teacher/layouts/SidebarView.vue";

const route = useRoute();

const isMobile = ref(false);
const checkScreen = () => {
  isMobile.value = window.innerWidth < 800;
};
onMounted(() => {
  checkScreen();
  window.addEventListener("resize", checkScreen);
});
onUnmounted(() => {
  window.removeEventListener("resize", checkScreen);
});

const sidebarWidth = computed(() => (isMobile.value ? "65px" : "250px"));
</script>

<template>
  <el-container>
    <el-aside :width="sidebarWidth">
      <TeacherSidebar :title="route.meta.title" />
    </el-aside>

    <el-container>
      <el-header v-if="!route.meta.noHeader">
        <TeacherHeader :title="route.meta.title" />
      </el-header>
      <Transition name="page" mode="out-in">
        <el-main :key="route.fullPath">
          <NuxtPage />
        </el-main>
      </Transition>
      <el-footer v-if="!route.meta.noHeader">
        <TeacherFooter :title="route.meta.title as string" />
      </el-footer>
    </el-container>
  </el-container>
</template>
<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.25s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
