<script setup lang="ts">
import StudentCard from "~/components/Cards/StudentCard.vue";
import TeacherCard from "~/components/Cards/TeacherCard.vue";
import AdminCard from "~/components/Cards/AdminCard.vue";

defineProps<{
  userCount?: {
    student: number;
    teacher: number;
    admin: number;
  };
  userGrowth?: {
    studentGrowth: number;
    teacherGrowth: number;
    adminGrowth: number;
  };
  normalCount?: {
    student?: number;
    teacher?: number;
    admin?: number;
  };
}>();
</script>

<template>
  <el-row :gutter="30">
    <el-col :span="8">
      <StudentCard
        :normal-count="normalCount?.student"
        :count="userCount?.student"
        :growth="userGrowth?.studentGrowth" />
    </el-col>
    <el-col :span="8">
      <TeacherCard
        :normal-count="normalCount?.teacher"
        :count="userCount?.teacher"
        :growth="userGrowth?.teacherGrowth" />
    </el-col>
    <el-col :span="8">
      <AdminCard
        :normal-count="normalCount?.admin"
        :count="userCount?.admin"
        :growth="userGrowth?.adminGrowth" />
    </el-col>
  </el-row>
</template>
