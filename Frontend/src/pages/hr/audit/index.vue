<script setup lang="ts">
import AuditLogTable from "~/components/hrms/audit/AuditLogTable.vue";

definePageMeta({ layout: "default" });
</script>

<template>
  <AuditLogTable
    title="HR Audit Logs"
    description="Central HRMS audit trail for employee, attendance, leave, overtime, and payroll actions."
    back-path="/hr"
  />
</template>
