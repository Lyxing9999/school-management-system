<script setup lang="ts">
import { computed, defineEmits, defineProps, reactive, ref, watch } from "vue";
import { useMessage } from "~/composables/common/useMessage";
const { showError } = useMessage();
const previousValues = ref<Record<string, string>>({});
const delayedHasDraft = ref(false);
const draftRows = ref<Row[]>([]);
const suppressChangeWatch = ref(false);
type Row = {
  key: string;
  value: string;
  originalKey: string;
  isDraft: boolean;
  dateOnly?: string;
  dateSuffix?: number | null;
  candidateKey?: string | null;
  confirmVisible?: boolean;
  dateSuffixEnabled?: boolean;
};

const props = defineProps<{
  modelValue: Record<string, string>;
  disabled?: boolean;
  draft?: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: Record<string, string>): void;
  (e: "save", value: Record<string, string>): void;
  (e: "update:draft", value: boolean): void;
  (e: "refresh"): void;
}>();

const statusOptions = [
  { label: "Present", value: "present" },
  { label: "Absent", value: "absent" },
  { label: "Late", value: "late" },
  { label: "Excused", value: "excused" },
];

const displayRows = computed(() => {
  const fromModel = Object.entries(props.modelValue || {})
    .filter(([key]) => key?.trim())
    .map(([key, value]) => ({
      key,
      value,
      originalKey: key,
      isDraft: false,
    }));
  return [...draftRows.value, ...fromModel].sort((a, b) => {
    const [dA, sufA = 0] = a.key.split("_");
    const [dB, sufB = 0] = b.key.split("_");
    const diff = new Date(dB).getTime() - new Date(dA).getTime();
    if (diff !== 0) return diff;
    return Number(sufB) - Number(sufA);
  });
});

function refreshDraftRows() {
  draftRows.value = draftRows.value.filter(
    (draft) => !(draft.key in props.modelValue)
  );
  emit("update:draft", draftRows.value.length > 0);
}

const patchValue = (key: string, value: string) => {
  const valid = statusOptions.map((s) => s.value);
  if (!valid.includes(value)) return;
  const oldValue = props.modelValue?.[key] ?? "";
  if (oldValue === value) return;
  const isNewDraft = draftRows.value.some((r) => r.key === key);
  if (isNewDraft) {
    delete previousValues.value[key];
  } else if (!(key in previousValues.value)) {
    previousValues.value[key] = oldValue;
  }

  suppressChangeWatch.value = true;
  const draftIndex = draftRows.value.findIndex((r) => r.key === key);
  if (draftIndex !== -1) {
    draftRows.value[draftIndex].isDraft = false;
  }
  const newObj = { ...props.modelValue, [key]: value };
  emit("update:modelValue", newObj);
  refreshDraftRows();
  emit("save", newObj);
  setTimeout(() => {
    suppressChangeWatch.value = false;
  }, 100);
};

function hasUnsavedChange(key: string) {
  return previousValues.value.hasOwnProperty(key);
}

const editableRows = ref<Row[]>([]);

const pendingChanges = computed(() =>
  editableRows.value.filter((row) => {
    if (row.isDraft) return false;

    const keyChanged = row.key !== row.originalKey;
    const oldValue = props.modelValue[row.originalKey];
    const valueChanged = row.value !== oldValue;

    return keyChanged || valueChanged;
  })
);

function saveAllChanges() {
  suppressChangeWatch.value = true;
  const updatedModel = { ...props.modelValue };

  for (const row of pendingChanges.value) {
    updatedModel[row.originalKey] = row.value;
    delete previousValues.value[row.originalKey];
  }
  emit("update:modelValue", updatedModel);
  refreshDraftRows();
  emit("save", updatedModel);
  setTimeout(() => {
    suppressChangeWatch.value = false;
  }, 100);
}

function undoChange(key: string) {
  const prev = previousValues.value[key];
  const isDraft = draftRows.value.some((r) => r.key === key);
  if (isDraft) {
    draftRows.value = draftRows.value.filter((r) => r.key !== key);
    editableRows.value = editableRows.value.filter((r) => r.key !== key);
    delete previousValues.value[key];
    emit("update:draft", draftRows.value.length > 0);
    return;
  }
  if (prev === undefined) return;
  const row = editableRows.value.find((r) => r.key === key);
  if (row) {
    row.value = prev;
  }
  const newObj = { ...props.modelValue, [key]: prev };
  delete previousValues.value[key];
}

const hasDraftRow = computed(() =>
  displayRows.value.some((row) => row.isDraft)
);

function isValidDateKey(dateKey: string) {
  return /^\d{4}-\d{2}-\d{2}(_\d+)?$/.test(dateKey);
}
const cancelAllChanges = () => {
  draftRows.value = [];
  previousValues.value = {};
  editableRows.value = displayRows.value.map((row) => ({
    ...row,
    originalKey: row.originalKey ?? row.key,
  }));
  emit("update:draft", false);
};

const searchQuery = ref("");

const filteredRows = computed(() => {
  if (!searchQuery.value.trim()) return editableRows.value;
  return editableRows.value.filter((row) =>
    row.key.includes(searchQuery.value.trim())
  );
});

watch(
  hasDraftRow,
  (val) => {
    delayedHasDraft.value = val;
  },
  { immediate: true }
);

watch(
  () => props.modelValue,
  () => {
    refreshDraftRows();
  }
);

watch(
  () => displayRows.value,
  (newRows) => {
    editableRows.value = newRows.map((row) => ({
      ...row,
      originalKey: row.key,
      dateOnly: row.key.split("_")[0],
      dateSuffix: row.key.includes("_") ? Number(row.key.split("_")[1]) : null,
      candidateKey: null,
      confirmVisible: false,
      dateSuffixEnabled: false,
    }));
  },
  { immediate: true, deep: true }
);

watch(
  editableRows,
  (rows) => {
    if (suppressChangeWatch.value) return;

    rows.forEach(({ key, value }) => {
      const original = props.modelValue[key];
      const changed = original !== value;

      if (changed) {
        previousValues.value[key] = original;
      } else {
        delete previousValues.value[key];
      }
    });
  },
  { deep: true }
);

function patchKey(oldKey: string, newKey: string): boolean {
  newKey = newKey.trim();
  if (!isValidDateKey(newKey)) {
    showError("Use format YYYY-MM-DD or YYYY-MM-DD_1");
    return false;
  }
  if (Object.keys(props.modelValue).some((k) => k !== oldKey && k === newKey)) {
    showError(`Duplicate key: ${newKey}`);
    return false;
  }
  const originalValue = props.modelValue[oldKey];
  if (originalValue === undefined) {
    showError("Original key not found.");
    return false;
  }
  const newObj = { ...props.modelValue };
  delete newObj[oldKey];
  newObj[newKey] = originalValue;
  emit("update:modelValue", newObj);
  emit("save", newObj);
  return true;
}

function onSuffixBlur(row: Row) {
  const suffix = row.dateSuffix ? `_${row.dateSuffix}` : "";
  const candidate = row.dateOnly + suffix;

  if (candidate !== row.originalKey) {
    row.candidateKey = candidate;
    row.confirmVisible = true;
  } else {
    row.candidateKey = null;
    row.confirmVisible = false;
  }
}
function onConfirm(row: Row) {
  if (!keyChanged(row)) return;
  const oldKey = row.originalKey;
  const newKey = row.candidateKey!;
  const success = patchKey(oldKey, newKey);
  if (!success) {
    onCancel(row);
    return;
  }
  row.originalKey = newKey;
  row.key = newKey;
  row.dateOnly = newKey.split("_")[0];
  row.dateSuffix = newKey.includes("_") ? Number(newKey.split("_")[1]) : null;
  row.confirmVisible = false;
  row.candidateKey = null;

  const picker = datePickers[newKey];
  if (picker) {
    if (typeof picker.hidePicker === "function") picker.hidePicker();
    const inputEl = picker.$el?.querySelector("input");
    if (inputEl) inputEl.blur();
  }
}

function onCancel(row: Row) {
  row.confirmVisible = false;
  row.candidateKey = null;
  const [, suf] = row.originalKey.split("_");
  row.dateSuffix = suf ? Number(suf) : null;
}

function keyChanged(row: Row) {
  return row.candidateKey != null && row.candidateKey !== row.originalKey;
}

const removeRowPatch = (key: string) => {
  const draftIndex = draftRows.value.findIndex((r) => r.key === key);
  if (draftIndex !== -1) {
    draftRows.value.splice(draftIndex, 1);
    emit("update:draft", draftRows.value.length > 0);
    return;
  }
  if (props.modelValue && key in props.modelValue) {
    const newObj = { ...props.modelValue };
    delete newObj[key];
    emit("update:modelValue", newObj);
    emit("save", newObj);
  }
};

const addKeyValuePair = () => {
  const today = new Date().toISOString().split("T")[0];
  let suffix = 1;
  let newKey = `${today}_${suffix}`;

  while (
    newKey in props.modelValue ||
    draftRows.value.some((r) => r.key === newKey)
  ) {
    suffix++;
    newKey = `${today}_${suffix}`;
  }

  draftRows.value.unshift({
    key: newKey,
    value: "present",
    originalKey: newKey,
    isDraft: true,
  });
  emit("update:draft", true);
};

const saveDraft = (oldKey: string, newKey: string | null, value: string) => {
  suppressChangeWatch.value = true;
  const finalKey = (newKey ?? oldKey).trim();
  if (!isValidDateKey(finalKey)) {
    showError("Use format YYYY-MM-DD or YYYY-MM-DD_1");
    suppressChangeWatch.value = false;
    return;
  }
  if (finalKey !== oldKey && finalKey in props.modelValue) {
    showError(`Key already exists: ${finalKey}`);
    suppressChangeWatch.value = false;
    return;
  }
  if (finalKey !== oldKey && oldKey in props.modelValue) {
    if (!patchKey(oldKey, finalKey)) {
      suppressChangeWatch.value = false;
      return;
    }
  }
  patchValue(finalKey, value);
  draftRows.value = draftRows.value.filter((r) => r.key !== oldKey);
  delete previousValues.value[finalKey];
  refreshDraftRows();

  suppressChangeWatch.value = false;
};
const datePickers = reactive<Record<string, any>>({});
function updateCandidateKeyAndShow(row: Row) {
  const suffix = row.dateSuffix ? `_${row.dateSuffix}` : "";
  row.candidateKey = row.dateOnly + suffix;

  row.confirmVisible = keyChanged(row);
}

function onDateChange(row: Row) {
  updateCandidateKeyAndShow(row);
  const picker = datePickers[row.key];
  if (picker?.hidePicker) {
    picker.hidePicker();
  }
}

function onSuffixInput(row: Row) {
  updateCandidateKeyAndShow(row);
}
</script>

<template>
  <div v-if="displayRows.length > 0">
    <el-input
      v-model="searchQuery"
      placeholder="Search by date (e.g. 2025-06)"
      clearable
      class="mb-2"
      size="small"
      style="width: 320px"
    />
    <el-table :data="filteredRows" border size="small" style="width: 100%">
      <el-table-column label="Date" width="280">
        <template #default="{ row }">
          <div class="flex items-center space-x-2">
            <el-date-picker
              v-model="row.dateOnly"
              type="date"
              ref="el => datePickers[row.key] = el"
              size="small"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              :disabled="disabled"
              placeholder="Pick date"
              @change="onDateChange(row)"
            />

            <div class="flex items-center space-x-2">
              <label>s</label>

              <el-input
                v-model="row.dateSuffix"
                type="number"
                size="small"
                style="width: 60px"
                placeholder="__"
                :disabled="!row.dateSuffixEnabled"
                @blur="onSuffixBlur(row)"
                @input="onSuffixInput(row)"
                min="1"
              />

              <el-button
                :type="row.dateSuffixEnabled ? 'primary' : 'text'"
                size="small"
                circle
                icon="Edit"
                @click="row.dateSuffixEnabled = !row.dateSuffixEnabled"
              />

              <el-popconfirm
                v-if="!row.isDraft && keyChanged(row)"
                title="Save this new key?"
                :visible.sync="row.confirmVisible"
                @confirm="onConfirm(row)"
                @cancel="onCancel(row)"
              >
                <template #reference>
                  <el-button type="success" icon="Check" size="small" circle />
                </template>
              </el-popconfirm>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="Status" width="100">
        <template #default="{ row }">
          <div class="flex items-center space-x-2">
            <el-select
              v-model="row.value"
              size="small"
              placeholder="Select status"
              :disabled="disabled"
              style="width: 100px"
            >
              <el-option
                v-for="option in statusOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="Actions" width="100">
        <template #default="{ row }">
          <div class="flex justify-center gap-2">
            <el-popconfirm
              v-if="row.isDraft"
              title="Save this record?"
              @confirm="saveDraft(row.originalKey, row.candidateKey, row.value)"
            >
              <template #reference>
                <el-button
                  type="success"
                  icon="Check"
                  size="small"
                  circle
                  :disabled="disabled"
                />
              </template>
            </el-popconfirm>

            <el-tooltip
              v-else-if="hasUnsavedChange(row.key)"
              :content="`previous status: ${previousValues[row.key]}`"
              placement="top"
            >
              <el-button
                type="text"
                icon="Refresh"
                size="small"
                circle
                :disabled="disabled"
                @click="undoChange(row.key)"
              />
            </el-tooltip>

            <el-popconfirm
              title="Delete this record?"
              @confirm="removeRowPatch(row.key)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  icon="Delete"
                  size="small"
                  circle
                  :disabled="disabled"
                />
              </template>
            </el-popconfirm>
          </div>
        </template>
      </el-table-column>
      <Transition name="fade">
        <el-table-column v-if="delayedHasDraft" label="Draft" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.isDraft" type="warning" size="small"
              >Draft</el-tag
            >
          </template>
        </el-table-column>
      </Transition>
    </el-table>
  </div>

  <el-empty v-else description="No attendance records yet" />
  <div class="p-4">
    <el-row :gutter="20">
      <el-col :span="8" align="left">
        <Transition name="fade">
          <el-button
            type="success"
            :icon="pendingChanges.length > 0 ? 'Check' : ''"
            class="mt-4"
            @click="saveAllChanges"
          >
            Save All
            {{ pendingChanges.length > 0 ? `(${pendingChanges.length})` : "" }}
          </el-button>
        </Transition>
      </el-col>
      <el-col :span="8" align="center">
        <Transition name="fade">
          <el-button
            v-if="pendingChanges.length > 0"
            type="primary"
            @click="cancelAllChanges"
            :disabled="disabled"
            class="mt-4"
          >
            Cancel All
          </el-button>
        </Transition>
      </el-col>
      <el-col :span="8">
        <el-button
          type="info"
          @click="addKeyValuePair"
          :disabled="disabled"
          class="mt-4"
        >
          + Add
        </el-button>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
    