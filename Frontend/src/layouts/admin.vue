<script setup lang="ts">
import AdminHeader from "~/views/admin/layouts/HeaderView.vue";
import AdminFooter from "~/views/admin/layouts/FooterView.vue";
import AdminSidebar from "~/views/admin/layouts/SidebarView.vue";

const route = useRoute();
</script>

<template>
  <el-container>
    <el-aside>
      <AdminSidebar />
    </el-aside>

    <el-container>
      <el-header v-if="!route.meta.noHeader">
        <AdminHeader />
      </el-header>
      <Transition name="page" mode="out-in">
        <el-main :key="route.fullPath">
          <NuxtPage />
        </el-main>
      </Transition>
      <el-footer v-if="!route.meta.noHeader">
        <AdminFooter />
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
