<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import { hrmsAdminService } from "~/api/hr_admin";
import type {
  AttendanceDTO,
  AttendanceStatus,
} from "~/api/hr_admin/attendance";
import type { WorkingScheduleDTO } from "~/api/hr_admin/schedule";

interface GeoCoordinates {
  latitude: number;
  longitude: number;
}

const attendanceService = hrmsAdminService().attendance;
const workingScheduleService = hrmsAdminService().workingSchedule;

const attendance = ref<AttendanceDTO | null>(null);
const currentLocalTime = ref(new Date());

const isLoadingAttendance = ref(false);
const isCheckingIn = ref(false);
const isCheckingOut = ref(false);

const pageError = ref("");
const actionError = ref("");
const geolocationError = ref("");
const scheduleError = ref("");
const wrongLocationReason = ref("");
const lateReasonDialogVisible = ref(false);
const lateReason = ref("");
const lateReasonError = ref("");
const earlyLeaveReasonDialogVisible = ref(false);
const earlyLeaveReason = ref("");
const earlyLeaveReasonError = ref("");

const pendingCheckInPayload = ref<{
  check_in_time: string;
  latitude: number;
  longitude: number;
  wrong_location_reason?: string | null;
} | null>(null);

const pendingCheckOutPayload = ref<{
  check_out_time: string;
  latitude: number;
  longitude: number;
} | null>(null);

const employeeSchedule = ref<WorkingScheduleDTO | null>(null);
const isLoadingSchedule = ref(false);

let clockInterval: ReturnType<typeof setInterval> | null = null;

const hasCheckedIn = computed(() => Boolean(attendance.value?.check_in_time));
const hasCheckedOut = computed(() => Boolean(attendance.value?.check_out_time));

const canCheckIn = computed(
  () =>
    !hasCheckedIn.value &&
    !isLoadingAttendance.value &&
    !isCheckingIn.value &&
    !isCheckingOut.value,
);

const canCheckOut = computed(
  () =>
    hasCheckedIn.value &&
    !hasCheckedOut.value &&
    !isLoadingAttendance.value &&
    !isCheckingIn.value &&
    !isCheckingOut.value,
);

const showWrongLocationPending = computed(
  () => attendance.value?.status === "wrong_location_pending",
);

const dayNameMap = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const scheduleShiftLabel = computed(() => {
  if (!employeeSchedule.value) return "-";
  const start = employeeSchedule.value.start_time?.slice(0, 5) || "-";
  const end = employeeSchedule.value.end_time?.slice(0, 5) || "-";
  return `${start} - ${end}`;
});

const scheduleWorkingDaysLabel = computed(() => {
  if (!employeeSchedule.value?.working_days?.length) return "-";
  return employeeSchedule.value.working_days
    .slice()
    .sort((a, b) => a - b)
    .map((day) => dayNameMap[day] ?? String(day))
    .join(", ");
});

const statusBadgeClasses = computed(() => {
  const map: Record<string, string> = {
    checked_in: "status-badge--info",
    checked_out: "status-badge--success",
    late: "status-badge--warning",
    early_leave: "status-badge--warning",
    absent: "status-badge--danger",
    holiday_off: "status-badge--info",
    weekend_off: "status-badge--neutral",
    wrong_location_pending: "status-badge--warning",
    wrong_location_approved: "status-badge--success",
    wrong_location_rejected: "status-badge--danger",
  };

  return map[attendance.value?.status ?? ""] ?? "status-badge--neutral";
});

const clockLabel = computed(() =>
  currentLocalTime.value.toLocaleString("en-US", {
    weekday: "short",
    month: "short",
    day: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }),
);

const formatDateTime = (iso?: string | null) => {
  if (!iso) return "-";

  return new Date(iso).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatDateOnly = (value?: string | null) => {
  if (!value) return "-";

  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split("-");
    return new Date(
      Number(year),
      Number(month) - 1,
      Number(day),
    ).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
  }

  return new Date(value).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
  });
};

const formatCoordinate = (value?: number | null) => {
  if (typeof value !== "number") return "-";
  return value.toFixed(6);
};

const checkInLat = computed(() => attendance.value?.check_in_latitude ?? null);
const checkInLng = computed(() => attendance.value?.check_in_longitude ?? null);
const checkOutLat = computed(
  () => attendance.value?.check_out_latitude ?? null,
);
const checkOutLng = computed(
  () => attendance.value?.check_out_longitude ?? null,
);

const hasCheckInCoordinates = computed(
  () =>
    typeof checkInLat.value === "number" &&
    typeof checkInLng.value === "number",
);

const hasCheckOutCoordinates = computed(
  () =>
    typeof checkOutLat.value === "number" &&
    typeof checkOutLng.value === "number",
);

const primaryMapUrl = computed(() => {
  if (hasCheckOutCoordinates.value) {
    return `https://maps.google.com/maps?q=${checkOutLat.value},${checkOutLng.value}&z=16&output=embed`;
  }

  if (hasCheckInCoordinates.value) {
    return `https://maps.google.com/maps?q=${checkInLat.value},${checkInLng.value}&z=16&output=embed`;
  }

  return "";
});

const checkInGoogleMapsUrl = computed(() => {
  if (!hasCheckInCoordinates.value) return "";
  return `https://www.google.com/maps?q=${checkInLat.value},${checkInLng.value}`;
});

const checkOutGoogleMapsUrl = computed(() => {
  if (!hasCheckOutCoordinates.value) return "";
  return `https://www.google.com/maps?q=${checkOutLat.value},${checkOutLng.value}`;
});

const formatStatusLabel = (status?: string | null) => {
  if (!status) return "Not Checked In";

  const map: Record<string, string> = {
    checked_in: "Checked In",
    checked_out: "Checked Out",
    late: "Late",
    early_leave: "Early Leave",
    absent: "Absent",
    holiday_off: "Holiday Off",
    weekend_off: "Weekend Off",
    wrong_location_pending: "Wrong Location Pending",
    wrong_location_approved: "Wrong Location Approved",
    wrong_location_rejected: "Wrong Location Rejected",
  };

  return map[status as AttendanceStatus] ?? status;
};

const resolveErrorMessage = (error: unknown) => {
  const e = error as {
    message?: string;
    response?: {
      status?: number;
      data?: { message?: string };
    };
  };

  return (
    e.response?.data?.message ||
    e.message ||
    "Something went wrong. Please try again."
  );
};

const isLateReasonRequiredError = (error: unknown) => {
  const e = error as {
    message?: string;
    response?: {
      data?: { message?: string; code?: string };
    };
  };

  const code = e.response?.data?.code?.toLowerCase() ?? "";
  const message =
    e.response?.data?.message?.toLowerCase() ?? e.message?.toLowerCase() ?? "";

  return (
    message.includes("late_reason is required") ||
    message.includes("late check-in reason") ||
    (code.includes("appbaseexception_error") && message.includes("late"))
  );
};

const isEarlyLeaveReasonRequiredError = (error: unknown) => {
  const e = error as {
    message?: string;
    response?: {
      data?: { message?: string; code?: string };
    };
  };

  const code = e.response?.data?.code?.toLowerCase() ?? "";
  const message =
    e.response?.data?.message?.toLowerCase() ?? e.message?.toLowerCase() ?? "";

  return (
    message.includes("early_leave_reason is required") ||
    message.includes("checking out early") ||
    (code.includes("appbaseexception_error") &&
      message.includes("early_leave_reason"))
  );
};

const getGeolocation = (): Promise<GeoCoordinates> =>
  new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported by your browser."));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (error) => {
        if (error.code === error.PERMISSION_DENIED) {
          reject(
            new Error(
              "Location permission was denied. Please allow location access and try again.",
            ),
          );
          return;
        }

        if (error.code === error.POSITION_UNAVAILABLE) {
          reject(
            new Error(
              "Unable to determine your location right now. Please try again.",
            ),
          );
          return;
        }

        if (error.code === error.TIMEOUT) {
          reject(new Error("Location request timed out. Please try again."));
          return;
        }

        reject(new Error("Failed to capture your location. Please try again."));
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0,
      },
    );
  });

const loadMyAttendance = async () => {
  isLoadingAttendance.value = true;
  pageError.value = "";
  scheduleError.value = "";

  try {
    const result = await attendanceService.getMyAttendanceToday({
      showError: false,
    });

    attendance.value = result.item ?? null;

    const scheduleId = attendance.value?.schedule_id;
    if (!scheduleId) {
      employeeSchedule.value = null;
      return;
    }

    isLoadingSchedule.value = true;
    try {
      employeeSchedule.value = await workingScheduleService.getSchedule(
        scheduleId,
        { showError: false },
      );
    } catch (scheduleLoadError) {
      employeeSchedule.value = null;
      scheduleError.value = resolveErrorMessage(scheduleLoadError);
    } finally {
      isLoadingSchedule.value = false;
    }
  } catch (error) {
    const message = resolveErrorMessage(error).toLowerCase();
    const status = (error as { response?: { status?: number } })?.response
      ?.status;

    if (
      status === 404 ||
      message.includes("not found") ||
      message.includes("no attendance")
    ) {
      attendance.value = null;
      employeeSchedule.value = null;
      return;
    }

    pageError.value = resolveErrorMessage(error);
  } finally {
    isLoadingAttendance.value = false;
  }
};

const handleRefresh = async () => {
  await loadMyAttendance();
};

const handleCheckIn = async () => {
  if (!canCheckIn.value) return;

  isCheckingIn.value = true;
  actionError.value = "";
  geolocationError.value = "";

  try {
    const location = await getGeolocation();
    const checkInTime = new Date().toISOString();
    const payload = {
      check_in_time: checkInTime,
      latitude: location.latitude,
      longitude: location.longitude,
      wrong_location_reason: wrongLocationReason.value.trim() || null,
    };

    pendingCheckInPayload.value = payload;

    await attendanceService.checkIn(payload);

    wrongLocationReason.value = "";
    lateReason.value = "";
    pendingCheckInPayload.value = null;
    await loadMyAttendance();
  } catch (error) {
    if (isLateReasonRequiredError(error)) {
      lateReasonError.value = "Please provide a reason for late check-in.";
      lateReasonDialogVisible.value = true;
      return;
    }

    const message = resolveErrorMessage(error);
    actionError.value = message;

    if (
      message.toLowerCase().includes("location") ||
      message.toLowerCase().includes("geolocation")
    ) {
      geolocationError.value = message;
    }
  } finally {
    isCheckingIn.value = false;
  }
};

const closeLateReasonDialog = () => {
  lateReasonDialogVisible.value = false;
  lateReasonError.value = "";
};

const submitLateReason = async () => {
  const reason = lateReason.value.trim();

  if (!reason) {
    lateReasonError.value = "Late reason is required.";
    return;
  }

  if (reason.length > 300) {
    lateReasonError.value = "Late reason must be 300 characters or less.";
    return;
  }

  if (!pendingCheckInPayload.value) {
    lateReasonError.value = "Check-in session expired. Please try again.";
    return;
  }

  isCheckingIn.value = true;
  lateReasonError.value = "";

  try {
    await attendanceService.checkIn({
      ...pendingCheckInPayload.value,
      late_reason: reason,
    });

    wrongLocationReason.value = "";
    lateReason.value = "";
    pendingCheckInPayload.value = null;
    closeLateReasonDialog();
    await loadMyAttendance();
  } catch (error) {
    const message = resolveErrorMessage(error);
    lateReasonError.value = message;
  } finally {
    isCheckingIn.value = false;
  }
};

const handleCheckOut = async () => {
  if (!canCheckOut.value) return;

  isCheckingOut.value = true;
  actionError.value = "";
  geolocationError.value = "";

  try {
    const location = await getGeolocation();
    const checkOutTime = new Date().toISOString();
    const payload = {
      check_out_time: checkOutTime,
      latitude: location.latitude,
      longitude: location.longitude,
    };

    pendingCheckOutPayload.value = payload;

    await attendanceService.checkOut(payload);

    earlyLeaveReason.value = "";
    pendingCheckOutPayload.value = null;
    await loadMyAttendance();
  } catch (error) {
    if (isEarlyLeaveReasonRequiredError(error)) {
      earlyLeaveReasonError.value =
        "Please provide a reason for early check-out.";
      earlyLeaveReasonDialogVisible.value = true;
      return;
    }

    const message = resolveErrorMessage(error);
    actionError.value = message;

    if (
      message.toLowerCase().includes("location") ||
      message.toLowerCase().includes("geolocation")
    ) {
      geolocationError.value = message;
    }
  } finally {
    isCheckingOut.value = false;
  }
};

const closeEarlyLeaveReasonDialog = () => {
  earlyLeaveReasonDialogVisible.value = false;
  earlyLeaveReasonError.value = "";
};

const submitEarlyLeaveReason = async () => {
  const reason = earlyLeaveReason.value.trim();

  if (!reason) {
    earlyLeaveReasonError.value = "Early leave reason is required.";
    return;
  }

  if (reason.length > 300) {
    earlyLeaveReasonError.value =
      "Early leave reason must be 300 characters or less.";
    return;
  }

  if (!pendingCheckOutPayload.value) {
    earlyLeaveReasonError.value =
      "Check-out session expired. Please try again.";
    return;
  }

  isCheckingOut.value = true;
  earlyLeaveReasonError.value = "";

  try {
    await attendanceService.checkOut({
      ...pendingCheckOutPayload.value,
      early_leave_reason: reason,
    });

    earlyLeaveReason.value = "";
    pendingCheckOutPayload.value = null;
    closeEarlyLeaveReasonDialog();
    await loadMyAttendance();
  } catch (error) {
    const message = resolveErrorMessage(error);
    earlyLeaveReasonError.value = message;
  } finally {
    isCheckingOut.value = false;
  }
};

onMounted(async () => {
  await loadMyAttendance();

  clockInterval = setInterval(() => {
    currentLocalTime.value = new Date();
  }, 1000);
});

onUnmounted(() => {
  if (clockInterval) clearInterval(clockInterval);
});
</script>

<template>
  <div class="attendance-today-page space-y-6 pb-10">
    <OverviewHeader
      :title="'My Attendance'"
      :description="'Check in and check out with GPS verification for accurate attendance records.'"
      :backPath="'/hr/attendance'"
    >
      <template #actions>
        <button
          type="button"
          class="btn btn-secondary rounded-lg px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="isLoadingAttendance || isCheckingIn || isCheckingOut"
          @click="handleRefresh"
        >
          Refresh
        </button>
      </template>
    </OverviewHeader>

    <section class="clock-hero rounded-2xl p-5 sm:p-6">
      <div class="flex items-center justify-between gap-4">
        <div>
          <p class="clock-hero__eyebrow">Local Time</p>
          <p class="clock-hero__time">
            {{ clockLabel }}
          </p>
          <p class="clock-hero__subtext">
            Live company local time for attendance actions
          </p>
        </div>

        <div class="clock-hero__badge">HRMS</div>
      </div>
    </section>

    <div
      v-if="pageError"
      class="alert alert-danger rounded-xl px-4 py-3 text-sm"
    >
      {{ pageError }}
    </div>

    <div class="grid gap-5 lg:grid-cols-2">
      <section class="panel-card rounded-2xl p-5 sm:p-6">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">
              Today&apos;s Attendance
            </h2>
            <p class="text-sm text-slate-500">
              Self-service summary for your current attendance day.
            </p>
          </div>
          <span
            class="status-badge inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset"
            :class="statusBadgeClasses"
          >
            {{ formatStatusLabel(attendance?.status) }}
          </span>
        </div>

        <div v-if="isLoadingAttendance" class="mt-5 animate-pulse space-y-3">
          <div class="skeleton h-10 rounded-lg" />
          <div class="skeleton h-10 rounded-lg" />
          <div class="skeleton h-10 rounded-lg" />
        </div>

        <div v-else-if="attendance" class="mt-5 space-y-4">
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div class="info-tile rounded-xl px-4 py-3">
              <p class="info-label">Attendance Date</p>
              <p class="info-value">
                {{ formatDateOnly(attendance.attendance_date) }}
              </p>
            </div>

            <div class="info-tile rounded-xl px-4 py-3">
              <p class="info-label">Check-In Time</p>
              <p class="info-value">
                {{ formatDateTime(attendance.check_in_time) }}
              </p>
            </div>

            <div class="info-tile rounded-xl px-4 py-3">
              <p class="info-label">Check-Out Time</p>
              <p class="info-value">
                {{ formatDateTime(attendance.check_out_time) }}
              </p>
            </div>

            <div class="info-tile rounded-xl px-4 py-3">
              <p class="info-label">Status</p>
              <p class="info-value">
                {{ formatStatusLabel(attendance.status) }}
              </p>
            </div>

            <div class="info-tile rounded-xl px-4 py-3">
              <p class="info-label">Late Minutes</p>
              <p class="info-value">
                {{ attendance.late_minutes ?? 0 }}
              </p>
            </div>

            <div class="info-tile rounded-xl px-4 py-3">
              <p class="info-label">Early Leave Minutes</p>
              <p class="info-value">
                {{ attendance.early_leave_minutes ?? 0 }}
              </p>
            </div>
          </div>

          <div class="surface-card rounded-xl p-4">
            <div class="mb-3 flex items-center justify-between gap-3">
              <h3 class="text-sm font-semibold text-slate-800">
                Today&apos;s Work Schedule
              </h3>
              <span
                class="chip chip-primary rounded-full px-2 py-0.5 text-xs font-medium"
              >
                {{ employeeSchedule?.name || "Not Assigned" }}
              </span>
            </div>

            <div v-if="isLoadingSchedule" class="grid gap-3 sm:grid-cols-3">
              <div class="skeleton h-14 rounded-lg" />
              <div class="skeleton h-14 rounded-lg" />
              <div class="skeleton h-14 rounded-lg" />
            </div>

            <div
              v-else-if="scheduleError"
              class="alert alert-warning rounded-lg px-3 py-2 text-sm"
            >
              {{ scheduleError }}
            </div>

            <div v-else-if="employeeSchedule" class="grid gap-3 sm:grid-cols-3">
              <div class="card-soft rounded-lg p-3">
                <p class="info-label">Shift Time</p>
                <p class="info-value">
                  {{ scheduleShiftLabel }}
                </p>
              </div>

              <div class="card-soft rounded-lg p-3">
                <p class="info-label">Working Days</p>
                <p class="info-value">
                  {{ scheduleWorkingDaysLabel }}
                </p>
              </div>

              <div class="card-soft rounded-lg p-3">
                <p class="info-label">Hours / Day</p>
                <p class="info-value">
                  {{ employeeSchedule.total_hours_per_day }} hrs
                </p>
              </div>
            </div>

            <div v-else class="empty-state rounded-lg px-3 py-3 text-sm">
              No schedule assigned for this attendance record.
            </div>
          </div>

          <div class="surface-card rounded-xl p-4">
            <div class="mb-3 flex items-center justify-between gap-3">
              <h3 class="text-sm font-semibold text-slate-800">
                Employee Location Map
              </h3>
              <span class="chip chip-muted rounded-full px-2 py-0.5 text-xs">
                {{
                  hasCheckOutCoordinates
                    ? "Checkout point"
                    : hasCheckInCoordinates
                    ? "Checkin point"
                    : "No point yet"
                }}
              </span>
            </div>

            <div
              v-if="primaryMapUrl"
              class="overflow-hidden rounded-xl border"
              style="border-color: var(--border-color)"
            >
              <iframe
                title="Employee Attendance Location"
                :src="primaryMapUrl"
                class="h-[240px] w-full"
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
              />
            </div>

            <div
              v-else
              class="empty-state rounded-xl px-4 py-6 text-center text-sm"
            >
              No recorded coordinates yet. After check-in/check-out, location
              will appear here.
            </div>

            <div class="mt-3 grid gap-3 sm:grid-cols-2">
              <div class="card-soft rounded-lg p-3">
                <p class="info-label">Check-In Coordinates</p>
                <p class="info-value">
                  {{ formatCoordinate(checkInLat) }},
                  {{ formatCoordinate(checkInLng) }}
                </p>
                <a
                  v-if="checkInGoogleMapsUrl"
                  :href="checkInGoogleMapsUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="theme-link mt-2 inline-block text-xs font-medium hover:underline"
                >
                  Open Check-In in Google Maps
                </a>
              </div>

              <div class="card-soft rounded-lg p-3">
                <p class="info-label">Check-Out Coordinates</p>
                <p class="info-value">
                  {{ formatCoordinate(checkOutLat) }},
                  {{ formatCoordinate(checkOutLng) }}
                </p>
                <a
                  v-if="checkOutGoogleMapsUrl"
                  :href="checkOutGoogleMapsUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="theme-link mt-2 inline-block text-xs font-medium hover:underline"
                >
                  Open Check-Out in Google Maps
                </a>
              </div>
            </div>
          </div>

          <div
            v-if="showWrongLocationPending"
            class="alert alert-warning rounded-xl px-4 py-3 text-sm"
          >
            Your check-in location is pending admin review. You can still
            monitor your status here.
          </div>
        </div>

        <div
          v-else
          class="empty-state mt-5 rounded-xl px-4 py-8 text-center text-sm"
        >
          No attendance record found for today yet. Use the action panel to
          check in.
        </div>
      </section>

      <section class="panel-card rounded-2xl p-5 sm:p-6">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">
            Attendance Actions
          </h2>
          <p class="text-sm text-slate-500">
            Your current time is automatically sent as ISO datetime on each
            action.
          </p>
        </div>

        <div
          v-if="geolocationError"
          class="alert alert-warning mt-4 rounded-xl px-4 py-3 text-sm"
        >
          {{ geolocationError }}
        </div>

        <div
          v-else-if="actionError"
          class="alert alert-danger mt-4 rounded-xl px-4 py-3 text-sm"
        >
          {{ actionError }}
        </div>

        <div class="mt-5 space-y-6">
          <div class="surface-card rounded-xl p-4">
            <div class="flex items-center justify-between">
              <h3
                class="text-sm font-semibold uppercase tracking-wide text-slate-700"
              >
                Check-In
              </h3>
              <span
                class="text-xs font-medium"
                :class="hasCheckedIn ? 'state-success' : 'state-muted'"
              >
                {{ hasCheckedIn ? "Completed" : "Pending" }}
              </span>
            </div>

            <label
              for="wrong-location-reason"
              class="mt-4 block text-sm font-medium text-slate-700"
            >
              Wrong Location Reason (Optional)
            </label>
            <textarea
              id="wrong-location-reason"
              v-model="wrongLocationReason"
              rows="3"
              class="theme-input mt-2 w-full rounded-lg px-3 py-2 text-sm outline-none transition disabled:cursor-not-allowed"
              :disabled="!canCheckIn"
              placeholder="If you are checking in from a different location, add a reason for admin review..."
            />

            <button
              type="button"
              class="btn btn-primary mt-4 w-full rounded-xl px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed"
              :disabled="!canCheckIn"
              @click="handleCheckIn"
            >
              {{
                isCheckingIn
                  ? "Checking In..."
                  : hasCheckedIn
                  ? "Already Checked In"
                  : "Check In Now"
              }}
            </button>
          </div>

          <div class="surface-card rounded-xl p-4">
            <div class="flex items-center justify-between">
              <h3
                class="text-sm font-semibold uppercase tracking-wide text-slate-700"
              >
                Check-Out
              </h3>
              <span
                class="text-xs font-medium"
                :class="hasCheckedOut ? 'state-success' : 'state-muted'"
              >
                {{ hasCheckedOut ? "Completed" : "Pending" }}
              </span>
            </div>

            <p class="mt-4 text-sm text-slate-500">
              Check-out also requires geolocation and sends the current datetime
              as ISO string.
            </p>

            <button
              type="button"
              class="btn btn-success mt-4 w-full rounded-xl px-4 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed"
              :disabled="!canCheckOut"
              @click="handleCheckOut"
            >
              {{
                isCheckingOut
                  ? "Checking Out..."
                  : hasCheckedOut
                  ? "Already Checked Out"
                  : "Check Out Now"
              }}
            </button>
          </div>
        </div>
      </section>
    </div>

    <el-dialog
      v-model="lateReasonDialogVisible"
      title="Late Check-In Reason"
      width="520px"
      @close="closeLateReasonDialog"
    >
      <div class="space-y-3">
        <p class="text-sm text-slate-600">
          Your check-in is marked as late. Please provide a reason to continue.
        </p>

        <label
          for="late-reason"
          class="block text-sm font-medium text-slate-700"
        >
          Late Reason
        </label>
        <textarea
          id="late-reason"
          v-model="lateReason"
          rows="4"
          maxlength="300"
          class="theme-input w-full rounded-lg px-3 py-2 text-sm outline-none transition"
          placeholder="Tell us why you checked in late..."
        />
        <div class="text-right text-xs text-slate-500">
          {{ lateReason.length }}/300
        </div>

        <div
          v-if="lateReasonError"
          class="alert alert-danger rounded-lg px-3 py-2 text-sm"
        >
          {{ lateReasonError }}
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <button
            type="button"
            class="btn btn-secondary rounded-lg px-4 py-2 text-sm font-medium"
            :disabled="isCheckingIn"
            @click="closeLateReasonDialog"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-primary rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed"
            :disabled="isCheckingIn"
            @click="submitLateReason"
          >
            {{ isCheckingIn ? "Submitting..." : "Submit Reason" }}
          </button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="earlyLeaveReasonDialogVisible"
      title="Early Check-Out Reason"
      width="520px"
      @close="closeEarlyLeaveReasonDialog"
    >
      <div class="space-y-3">
        <p class="text-sm text-slate-600">
          You are checking out early. Please provide a reason to continue.
        </p>

        <label
          for="early-leave-reason"
          class="block text-sm font-medium text-slate-700"
        >
          Early Leave Reason
        </label>
        <textarea
          id="early-leave-reason"
          v-model="earlyLeaveReason"
          rows="4"
          maxlength="300"
          class="theme-input w-full rounded-lg px-3 py-2 text-sm outline-none transition"
          placeholder="Tell us why you need to check out early..."
        />
        <div class="text-right text-xs text-slate-500">
          {{ earlyLeaveReason.length }}/300
        </div>

        <div
          v-if="earlyLeaveReasonError"
          class="alert alert-danger rounded-lg px-3 py-2 text-sm"
        >
          {{ earlyLeaveReasonError }}
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <button
            type="button"
            class="btn btn-secondary rounded-lg px-4 py-2 text-sm font-medium"
            :disabled="isCheckingOut"
            @click="closeEarlyLeaveReasonDialog"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-success rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed"
            :disabled="isCheckingOut"
            @click="submitEarlyLeaveReason"
          >
            {{ isCheckingOut ? "Submitting..." : "Submit Reason" }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>
<style>
/* Theme variables for light and dark mode */
:root {
  --theme-primary: #2563eb;
  --theme-primary-hover: #1d4ed8;
  --theme-primary-soft: #e0e7ff;
  --theme-primary-soft-2: #c7d2fe;
  --theme-primary-ring: rgba(37, 99, 235, 0.22);
  --theme-link: #2563eb;

  --theme-success: #22c55e;
  --theme-success-hover: #16a34a;
  --theme-success-soft: #dcfce7;

  --theme-warning: #f59e42;
  --theme-warning-soft: #fef3c7;
  --theme-warning-border: #fbbf24;

  --theme-danger: #ef4444;
  --theme-danger-soft: #fee2e2;
  --theme-danger-border: #f87171;

  --theme-muted-bg: #f3f4f6;
  --theme-muted-bg-2: #e5e7eb;
  --theme-muted-bg-3: #d1d5db;
  --theme-muted-text: #6b7280;

  --color-card: #fff;
  --surface-soft: #f9fafb;
  --border-color: #e5e7eb;
  --text-color: #1e293b;
  --muted-color: #64748b;
  --input-bg: #fff;
  --input-border: #cbd5e1;
  --btn-disabled-bg: #f1f5f9;
  --btn-disabled-text: #94a3b8;
  --color-light: #fff;
  --card-shadow: rgba(30, 41, 59, 0.06);
  --hover-bg: #f3f4f6;

  --status-success: #22c55e;
  --status-success-bg: #dcfce7;
  --status-success-border: #16a34a;
  --status-warning: #f59e42;
  --status-warning-bg: #fef3c7;
  --status-warning-border: #fbbf24;
  --status-danger: #ef4444;
  --status-danger-bg: #fee2e2;
  --status-danger-border: #f87171;
  --status-info: #2563eb;
  --status-info-bg: #e0e7ff;
  --status-info-border: #2563eb;
  --status-neutral: #64748b;
  --status-neutral-bg: #f3f4f6;
  --status-neutral-border: #cbd5e1;
}

@media (prefers-color-scheme: dark) {
  :root {
    --theme-primary: #60a5fa;
    --theme-primary-hover: #3b82f6;
    --theme-primary-soft: #1e293b;
    --theme-primary-soft-2: #334155;
    --theme-primary-ring: rgba(96, 165, 250, 0.22);
    --theme-link: #60a5fa;

    --theme-success: #4ade80;
    --theme-success-hover: #22c55e;
    --theme-success-soft: #052e16;

    --theme-warning: #fbbf24;
    --theme-warning-soft: #78350f;
    --theme-warning-border: #f59e42;

    --theme-danger: #f87171;
    --theme-danger-soft: #7f1d1d;
    --theme-danger-border: #ef4444;

    --theme-muted-bg: #1e293b;
    --theme-muted-bg-2: #334155;
    --theme-muted-bg-3: #475569;
    --theme-muted-text: #cbd5e1;

    --color-card: #0f172a;
    --surface-soft: #1e293b;
    --border-color: #334155;
    --text-color: #f1f5f9;
    --muted-color: #94a3b8;
    --input-bg: #1e293b;
    --input-border: #334155;
    --btn-disabled-bg: #334155;
    --btn-disabled-text: #64748b;
    --color-light: #f1f5f9;
    --card-shadow: rgba(2, 6, 23, 0.32);
    --hover-bg: #334155;

    --status-success: #4ade80;
    --status-success-bg: #052e16;
    --status-success-border: #22c55e;
    --status-warning: #fbbf24;
    --status-warning-bg: #78350f;
    --status-warning-border: #f59e42;
    --status-danger: #f87171;
    --status-danger-bg: #7f1d1d;
    --status-danger-border: #ef4444;
    --status-info: #60a5fa;
    --status-info-bg: #1e293b;
    --status-info-border: #60a5fa;
    --status-neutral: #94a3b8;
    --status-neutral-bg: #1e293b;
    --status-neutral-border: #334155;
  }
}

.attendance-today-page {
  padding: 1.5rem;
  max-width: 1520px;
  margin: 0 auto;
  color: var(--text-color);
}

.panel-card {
  border: 1px solid var(--border-color);
  background: var(--color-card);
  box-shadow: 0 10px 24px var(--card-shadow);
  transition: border-color 0.22s ease, box-shadow 0.22s ease,
    transform 0.22s ease;
}

.panel-card:hover {
  border-color: color-mix(
    in srgb,
    var(--border-color) 70%,
    var(--theme-primary) 30%
  );
  box-shadow: 0 14px 30px var(--card-shadow);
  transform: translateY(-1px);
}

.surface-card {
  border: 1px solid var(--border-color);
  background: var(--surface-soft);
}

.card-soft {
  border: 1px solid var(--border-color);
  background: var(--color-card);
}

.info-tile {
  border: 1px solid var(--border-color);
  background: var(--surface-soft);
}

.info-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted-color);
}

.info-value {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
}

.empty-state {
  border: 1px dashed var(--border-color);
  background: var(--color-card);
  color: var(--muted-color);
}

.clock-hero {
  border: 1px solid var(--theme-primary);
  background: linear-gradient(
    135deg,
    var(--theme-primary) 0%,
    var(--color-primary-light-1) 55%,
    var(--color-primary-light-2) 100%
  );
  box-shadow: 0 10px 24px
    color-mix(in srgb, var(--theme-primary) 30%, transparent);
}

.clock-hero__eyebrow {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #fff;
  opacity: 0.95;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.clock-hero__time {
  margin-top: 0.55rem;
  font-size: clamp(1.6rem, 2.5vw, 2.4rem);
  line-height: 1.2;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

.clock-hero__subtext {
  margin-top: 0.45rem;
  font-size: 0.92rem;
  color: #fff;
  opacity: 0.92;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.clock-hero__badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 74px;
  height: 36px;
  padding: 0 14px;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(8px);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.status-badge {
  border-color: transparent;
}

.status-badge--success {
  color: var(--status-success);
  background: var(--status-success-bg);
  box-shadow: inset 0 0 0 1px var(--status-success-border);
}

.status-badge--warning {
  color: var(--status-warning);
  background: var(--status-warning-bg);
  box-shadow: inset 0 0 0 1px var(--status-warning-border);
}

.status-badge--danger {
  color: var(--status-danger);
  background: var(--status-danger-bg);
  box-shadow: inset 0 0 0 1px var(--status-danger-border);
}

.status-badge--info {
  color: var(--status-info);
  background: var(--status-info-bg);
  box-shadow: inset 0 0 0 1px var(--status-info-border);
}

.status-badge--neutral {
  color: var(--status-neutral);
  background: var(--status-neutral-bg);
  box-shadow: inset 0 0 0 1px var(--status-neutral-border);
}

.btn {
  transition: all 0.2s ease !important;
}

.btn:not(:disabled):hover {
  transform: translateY(-1px);
}

.btn:disabled {
  background: var(--btn-disabled-bg) !important;
  color: var(--btn-disabled-text, var(--muted-color)) !important;
}

.btn-primary {
  background: var(--theme-primary);
}

.btn-primary:hover:not(:disabled) {
  background: var(--theme-primary-hover);
}

.btn-success {
  background: var(--theme-success);
}

.btn-success:hover:not(:disabled) {
  background: var(--theme-success-hover);
}

.btn-secondary {
  border: 1px solid var(--border-color);
  background: var(--color-card);
  color: var(--text-color);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--hover-bg);
}

.alert {
  border: 1px solid transparent;
}

.alert-danger {
  border-color: var(--theme-danger-border);
  background: var(--theme-danger-soft);
  color: var(--theme-danger);
}

.alert-warning {
  border-color: var(--theme-warning-border);
  background: var(--theme-warning-soft);
  color: var(--theme-warning);
}

.chip {
  display: inline-flex;
  align-items: center;
}

.chip-primary {
  background: var(--theme-primary-soft);
  color: var(--theme-primary);
}

.chip-muted {
  background: var(--theme-muted-bg-3);
  color: var(--text-color);
}

.theme-link {
  color: var(--theme-link);
}

.state-success {
  color: var(--theme-success);
}

.state-muted {
  color: var(--muted-color);
}

.theme-input {
  background-color: var(--input-bg) !important;
  border: 1px solid var(--input-border) !important;
  color: var(--text-color) !important;
}

.theme-input:focus {
  border-color: var(--theme-primary) !important;
  box-shadow: 0 0 0 2px var(--theme-primary-ring) !important;
}

.theme-input:disabled {
  background-color: var(--btn-disabled-bg) !important;
  color: var(--btn-disabled-text) !important;
  cursor: not-allowed !important;
}

.skeleton {
  background-color: var(--theme-muted-bg-2);
}

/* Theme overrides for existing Tailwind utility classes still in template */
.attendance-today-page :deep(.bg-white) {
  background-color: var(--color-card) !important;
}

.attendance-today-page :deep(.bg-slate-50) {
  background-color: var(--surface-soft) !important;
}

.attendance-today-page :deep(.bg-slate-100) {
  background-color: var(--theme-muted-bg-2) !important;
}

.attendance-today-page :deep(.bg-slate-200) {
  background-color: var(--theme-muted-bg-3) !important;
}

.attendance-today-page :deep(.border-slate-200),
.attendance-today-page :deep(.border-slate-300),
.attendance-today-page :deep(.border-dashed) {
  border-color: var(--border-color) !important;
}

.attendance-today-page :deep(.text-slate-900),
.attendance-today-page :deep(.text-slate-800),
.attendance-today-page :deep(.text-slate-700) {
  color: var(--text-color) !important;
}

.attendance-today-page :deep(.text-slate-600),
.attendance-today-page :deep(.text-slate-500) {
  color: var(--muted-color) !important;
}

.attendance-today-page :deep(.text-white) {
  color: var(--color-light) !important;
}

.attendance-today-page :deep(.disabled\:cursor-not-allowed:disabled) {
  cursor: not-allowed !important;
}

.attendance-today-page :deep(.disabled\:opacity-60:disabled) {
  opacity: 0.6 !important;
}

.attendance-today-page :deep(textarea),
.attendance-today-page :deep(input[type="text"]) {
  background-color: var(--input-bg) !important;
  border-color: var(--input-border) !important;
  color: var(--text-color) !important;
}

.attendance-today-page :deep(textarea:focus),
.attendance-today-page :deep(input[type="text"]:focus) {
  border-color: var(--theme-primary) !important;
  box-shadow: 0 0 0 2px var(--theme-primary-ring) !important;
}

.attendance-today-page :deep(textarea:disabled),
.attendance-today-page :deep(input[type="text"]:disabled) {
  background-color: var(--btn-disabled-bg) !important;
  color: var(--btn-disabled-text) !important;
  cursor: not-allowed !important;
}

.attendance-today-page :deep(.animate-pulse) {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
