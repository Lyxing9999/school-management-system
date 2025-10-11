<script setup lang="ts">
import { reactive, ref, watch } from "vue";
import { ElInput, ElForm, ElFormItem } from "element-plus";
import type { Field } from "../types/form";
import type { FormInstance } from "element-plus";
import DisplayOnlyField from "~/components/Form/DisplayOnlyField.vue";
const props = defineProps<{
  modelValue: Record<string, any>;
  useElForm: boolean;
  fields: Field[];
}>();

const emit = defineEmits<{
  (
    e: "save",
    form: Record<string, any>,
    elFormRef: FormInstance | undefined
  ): void;
  (
    e: "cancel",
    form: Record<string, any>,
    elFormRef: FormInstance | undefined
  ): void;
  (e: "update:modelValue", value: Record<string, any>): void;
}>();

const form = reactive({ ...props.modelValue });
const elFormRef = ref<FormInstance>();

watch(
  () => props.modelValue,
  (val) => {
    Object.assign(form, val);
  },
  { deep: true }
);

watch(form, (val) => emit("update:modelValue", { ...val }), { deep: true });

const getOptionsForField = (field: Field) => {
  const rawOptions =
    typeof field.childComponentProps?.options === "function"
      ? field.childComponentProps.options()
      : field.childComponentProps?.options?.value || [];
  return rawOptions.map((opt) => ({ value: opt.value, label: opt.label }));
};
</script>

<template>
  <component :is="useElForm ? ElForm : 'div'" :model="form" ref="elFormRef">
    <template v-for="(field, index) in fields" :key="index">
      <!-- Row fields: multiple inline -->
      <el-row v-if="field.row" :gutter="20" class="mb-4">
        <el-col
          v-for="subField in field.row"
          :key="subField.key"
          :span="24 / field.row.length"
        >
          <ElFormItem
            v-if="useElForm"
            :label="subField.label"
            :prop="subField.key"
            :label-width="subField.labelWidth"
            :label-position="subField.labelPosition"
            :rules="subField.rules"
          >
            <!-- Label with optional icon -->
            <template #label>
              <div style="display: flex; align-items: center; gap: 4px">
                <el-icon v-if="subField.iconComponent">
                  <component :is="subField.iconComponent" />
                </el-icon>
                <span>{{ subField.label }}</span>
              </div>
            </template>

            <!-- Display-only mode -->
            <template v-if="subField.displayOnly">
              <slot name="displayOnly" :value="form[subField.key]">
                <DisplayOnlyField :value="form[subField.key]" />
              </slot>
            </template>

            <!-- Editable field -->
            <component
              v-else
              v-model="form[subField.key]"
              :is="subField.component || ElInput"
              v-bind="subField.componentProps"
            >
              <component
                v-for="opt in getOptionsForField(subField)"
                :is="subField.childComponent"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </component>
          </ElFormItem>
        </el-col>
      </el-row>

      <!-- Single field fallback -->
      <ElFormItem
        v-else
        :label="field.label"
        :prop="field.key"
        :label-width="field.labelWidth"
        :label-position="field.labelPosition"
        :rules="field.rules"
        class="mb-4"
      >
        <!-- Label with optional icon -->
        <template #label>
          <div style="display: flex; align-items: center; gap: 4px">
            <el-icon v-if="field.iconComponent">
              <component :is="field.iconComponent" />
            </el-icon>
            <span>{{ field.label }}</span>
          </div>
        </template>

        <!-- Display-only mode -->
        <template v-if="field.displayOnly">
          <slot name="displayOnly" :value="form[field.key]">
            <DisplayOnlyField :value="form[field.key]" />
          </slot>
        </template>

        <!-- Editable field -->
        <component
          v-else
          v-model="form[field.key]"
          :is="field.component || ElInput"
          v-bind="field.componentProps"
        >
          <component
            v-for="opt in getOptionsForField(field)"
            :is="field.childComponent"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </component>
      </ElFormItem>
    </template>

    <!-- Operation buttons -->
    <template v-if="$slots.operation">
      <slot name="operation" :form="form" :elFormRef="elFormRef" />
    </template>
    <template v-else>
      <div class="flex justify-end gap-2 mt-4">
        <BaseButton type="default" @click="emit('cancel', form, elFormRef)">
          Cancel
        </BaseButton>
        <BaseButton
          type="info"
          class="w-20"
          @click="emit('save', form, elFormRef)"
        >
          Save
        </BaseButton>
      </div>
    </template>
  </component>
</template>
