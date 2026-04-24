<script setup lang="ts">
import AuditLogTable from "~/components/hrms/audit/AuditLogTable.vue";

definePageMeta({ layout: "default" });
</script>

<template>
  <AuditLogTable
    title="Manager Audit Logs"
    description="Review manager-visible HRMS actions across attendance, overtime, leave, and payroll records."
    back-path="/manager/dashboard"
  />
</template>
