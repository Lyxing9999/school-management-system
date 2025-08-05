<script setup lang="ts">
import { ref, computed } from "vue";
import DateRangeSelector from "~/components/Base/DateRangeSelector.vue";
import type {
  DateRangeType,
  FormattedDatesPayload,
} from "~/components/Base/DateRangeSelector.vue";
import StatisticsCards from "~/components/Base/StatisticsCards.vue";
import { UserService } from "~/services/userService";
import type { AxiosInstance } from "axios";

definePageMeta({ layout: "admin" });
type GrowthStat = {
  role: "student" | "admin" | "teacher";
  growth_percentage: number | string;
  current: number | string;
};

type NormalUserCount = {
  student: number;
  teacher: number;
  admin: number;
};

const adminGrowth = ref(0);
const teacherGrowth = ref(0);
const studentGrowth = ref(0);
const currentAdminCount = ref(0);
const currentTeacherCount = ref(0);
const currentStudentCount = ref(0);
const mode = ref("growth");

const processGrowthStats = (growthStatsArray: GrowthStat[]) => {
  adminGrowth.value = 0;
  teacherGrowth.value = 0;
  studentGrowth.value = 0;
  currentAdminCount.value = 0;
  currentTeacherCount.value = 0;
  currentStudentCount.value = 0;

  growthStatsArray.forEach((item) => {
    switch (item.role) {
      case "student":
        studentGrowth.value = Number(item.growth_percentage);
        currentStudentCount.value = Number(item.current);
        break;
      case "admin":
        adminGrowth.value = Number(item.growth_percentage);
        currentAdminCount.value = Number(item.current);
        break;
      case "teacher":
        teacherGrowth.value = Number(item.growth_percentage);
        currentTeacherCount.value = Number(item.current);
        break;
      default:
        console.warn(`Unknown role encountered: ${item.role}`);
    }
  });
};

const growthPercentages = computed(() => ({
  studentGrowth: studentGrowth.value,
  teacherGrowth: teacherGrowth.value,
  adminGrowth: adminGrowth.value,
}));
const growthUserCounts = computed(() => ({
  student: currentStudentCount.value,
  teacher: currentTeacherCount.value,
  admin: currentAdminCount.value,
}));

const handleRangeChange = (
  dates: FormattedDatesPayload,
  type: DateRangeType
) => {
  if (type === "all") {
    mode.value = "all";
    fetchNormal();
  } else {
    mode.value = "growth";
    fetchGrowth(dates);
  }
};

const fetchGrowth = async (dates: any) => {
  const $api = useNuxtApp().$api as AxiosInstance;
  const userService = new UserService($api);
  try {
    const growthStats = await userService.compareGrowthStatsByRole(dates);

    let growthStatsArray: GrowthStat[] = [];

    if (Array.isArray(growthStats)) {
      growthStatsArray = growthStats;
    } else if (typeof growthStats === "object" && growthStats !== null) {
      growthStatsArray = Object.entries(growthStats).map(([role, growth]) => ({
        role: role as "student" | "admin" | "teacher",
        growth_percentage: growth,
        current: 0,
      }));
    }

    processGrowthStats(growthStatsArray);
    console.log("User growth stats fetched successfully:", growthStatsArray);
  } catch (error) {
    console.error("Failed to fetch user growth stats:", error);
  }
  console.log("Parent received formatted dates:", dates);
};

const regularUserCounts = ref<NormalUserCount>({
  student: 0,
  teacher: 0,
  admin: 0,
});

const fetchNormal = async () => {
  const $api = useNuxtApp().$api as AxiosInstance;
  const userService = new UserService($api);
  try {
    const userCounts = await userService.countByRole();
    regularUserCounts.value = {
      student: userCounts.student,
      teacher: userCounts.teacher,
      admin: userCounts.admin,
    };
  } catch (error) {
    console.error("Failed to fetch normal user counts:", error);
  }
};
</script>

<template>
  <div class="p-4">
    <DateRangeSelector @formattedDates="handleRangeChange" />
  </div>

  <StatisticsCards
    v-if="mode === 'growth'"
    :user-count="growthUserCounts"
    :user-growth="growthPercentages"
  />

  <StatisticsCards v-else :normal-count="regularUserCounts" />
</template>
