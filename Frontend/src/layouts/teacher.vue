<script setup lang="ts">
import { useRoute } from "vue-router";
import BaseHeader from "~/components/layout/BaseHeader.vue";
import BaseFooter from "~/components/layout/BaseFooter.vue";
import BaseSideBar from "~/components/layout/BaseSideBar.vue";
import schoolLogo from "~/assets/image/school-logo.png";

const route = useRoute();
</script>

<template>
  <el-container>
    <el-aside width="250px">
      <BaseSideBar :logoSrc="schoolLogo" />
    </el-aside>

    <el-container>
      <el-header v-if="!route.meta.noHeader">
        <BaseHeader />
      </el-header>
      <Transition name="page" mode="out-in">
        <el-main :key="route.fullPath">
          <NuxtPage />
        </el-main>
      </Transition>
      <el-footer v-if="!route.meta.noHeader">
        <BaseFooter />
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
