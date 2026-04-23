<script setup lang="ts">
import { ref, computed, onMounted, onActivated } from "vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import { ROUTES } from "~/constants/routes";

definePageMeta({ layout: "default" });

const router = useRouter();
const hrService = hrmsAdminService();

const loading = ref(false);
const initialized = ref(false);

const teamAttendance = ref([]);
const pendingOT = ref([]);
const pendingLeave = ref([]);

// Summary stats
const teamStats = computed(() => ({
  present: teamAttendance.value.filter((a) => a.status === "present").length,
  late: teamAttendance.value.filter((a) => a.status === "late").length,
  absent: teamAttendance.value.filter((a) => a.status === "absent").length,
  total: teamAttendance.value.length,
}));

const otStats = computed(() => ({
  pending: pendingOT.value.length,
}));

const leaveStats = computed(() => ({
  pending: pendingLeave.value.length,
}));

async function fetchDashboard() {
  loading.value = true;
  try {
    const [attendanceRes, otRes, leaveRes] = await Promise.all([
      hrService.attendance.getTeamAttendances(),
      hrService.overtimeRequest.getPendingRequests(),
      hrService.leaveRequest.getPendingRequests(),
    ]);
    teamAttendance.value = attendanceRes.items ?? [];
    pendingOT.value = otRes.items ?? [];
    pendingLeave.value = leaveRes.items ?? [];
  } catch (e) {
    // handled by service layer
  } finally {
    loading.value = false;
  }
}

async function ensureInitialLoad() {
  if (initialized.value) return;
  initialized.value = true;
  await fetchDashboard();
}

onMounted(() => {
  void ensureInitialLoad();
});

onActivated(() => {
  void fetchDashboard();
});
</script>

<template>
  <div class="manager-dashboard-page">
    <OverviewHeader
      title="Manager Dashboard"
      description="Team attendance, pending overtime, and leave reviews"
      :backPath="ROUTES.MANAGER.DASHBOARD"
    >
      <template #actions>
        <BaseButton plain :loading="loading" @click="fetchDashboard">
          Refresh
        </BaseButton>
      </template>
    </OverviewHeader>

    <el-row :gutter="16" class="section-row section-row--kpi">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card
          class="panel-card kpi-card kpi-card--attendance"
          shadow="hover"
          v-loading="loading"
        >
          <p class="kpi-card__label">Team Present</p>
          <p class="kpi-card__value">{{ teamStats.present }}</p>
          <p class="kpi-card__hint">Total: {{ teamStats.total }}</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card
          class="panel-card kpi-card kpi-card--late"
          shadow="hover"
          v-loading="loading"
        >
          <p class="kpi-card__label">Late</p>
          <p class="kpi-card__value">{{ teamStats.late }}</p>
          <p class="kpi-card__hint">Today</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card
          class="panel-card kpi-card kpi-card--ot"
          shadow="hover"
          v-loading="loading"
        >
          <p class="kpi-card__label">Pending OT Approvals</p>
          <p class="kpi-card__value">{{ otStats.pending }}</p>
          <p class="kpi-card__hint">Action Required</p>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card
          class="panel-card kpi-card kpi-card--leave"
          shadow="hover"
          v-loading="loading"
        >
          <p class="kpi-card__label">Pending Leave Reviews</p>
          <p class="kpi-card__value">{{ leaveStats.pending }}</p>
          <p class="kpi-card__hint">Action Required</p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="section-row">
      <el-col :xs="24" :lg="12">
        <el-card
          shadow="hover"
          class="panel-card dashboard-card"
          v-loading="loading"
        >
          <div class="card-top">
            <div>
              <div class="section-head">Team Attendance</div>
              <div class="section-sub">
                Today’s attendance status for all team members
              </div>
            </div>
          </div>
          <div class="table-wrap">
            <el-table
              :data="teamAttendance"
              size="small"
              border
              style="width: 100%"
            >
              <el-table-column
                prop="employee_name"
                label="Name"
                min-width="140"
              />
              <el-table-column prop="status" label="Status" min-width="110" />
              <el-table-column
                prop="check_in_time"
                label="Check In"
                min-width="120"
              />
              <el-table-column
                prop="check_out_time"
                label="Check Out"
                min-width="120"
              />
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card
          shadow="hover"
          class="panel-card dashboard-card"
          v-loading="loading"
        >
          <div class="card-top">
            <div>
              <div class="section-head">Pending Overtime Approvals</div>
              <div class="section-sub">Requests awaiting your approval</div>
            </div>
          </div>
          <div class="table-wrap">
            <el-table :data="pendingOT" size="small" border style="width: 100%">
              <el-table-column
                prop="employee_name"
                label="Name"
                min-width="140"
              />
              <el-table-column prop="date" label="Date" min-width="110" />
              <el-table-column prop="hours" label="Hours" min-width="80" />
              <el-table-column prop="reason" label="Reason" min-width="160" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="section-row">
      <el-col :xs="24">
        <el-card
          shadow="hover"
          class="panel-card dashboard-card"
          v-loading="loading"
        >
          <div class="card-top">
            <div>
              <div class="section-head">Pending Leave Reviews</div>
              <div class="section-sub">Leave requests awaiting your review</div>
            </div>
          </div>
          <div class="table-wrap">
            <el-table
              :data="pendingLeave"
              size="small"
              border
              style="width: 100%"
            >
              <el-table-column
                prop="employee_name"
                label="Name"
                min-width="140"
              />
              <el-table-column prop="leave_type" label="Type" min-width="110" />
              <el-table-column
                prop="start_date"
                label="Start"
                min-width="110"
              />
              <el-table-column prop="end_date" label="End" min-width="110" />
              <el-table-column prop="reason" label="Reason" min-width="160" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.manager-dashboard-page {
  padding: 16px;
  max-width: 1460px;
  margin: 0 auto;
}
.section-row {
  margin-bottom: 16px;
}
.panel-card {
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: var(--color-card);
  transition: border-color 0.22s ease, box-shadow 0.22s ease,
    transform 0.22s ease;
}
.kpi-card__label {
  font-size: 15px;
  color: var(--muted-color, #64748b);
  margin-bottom: 2px;
}
.kpi-card__value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-color, #0f172a);
}
.kpi-card__hint {
  font-size: 13px;
  color: var(--muted-color, #64748b);
}
.table-wrap {
  margin-top: 12px;
}
</style>
