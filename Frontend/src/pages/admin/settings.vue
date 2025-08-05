<script setup lang="ts">
definePageMeta({
  layout: "admin",
});

import AdvancedUserTable from "~/views/admin/ManageUser/UserTable.vue";
</script>

<template>
  <el-card>
    <AdvancedUserTable />
  </el-card>
</template>
