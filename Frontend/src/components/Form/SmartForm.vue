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
</script>

<template>
  <component :is="useElForm ? ElForm : 'div'" :model="form" ref="elFormRef">
    <component
      v-for="field in fields"
      :is="useElForm ? ElFormItem : 'div'"
      :key="field.key"
      :label="field.label"
      :prop="field.key"
      :label-width="field.labelWidth"
      :label-position="field.labelPosition"
      :rules="field.rules"
    >
      <template #label>
        <div style="display: flex; align-items: center; gap: 4px">
          <el-icon v-if="field.iconComponent">
            <component :is="field.iconComponent" />
          </el-icon>
          <span>{{ field.label }}</span>
        </div>
      </template>

      <template v-if="field.displayOnly">
        <slot name="displayOnly" :value="form[field.key]">
          <DisplayOnlyField :value="form[field.key]" />
        </slot>
      </template>

      <component
        v-else
        v-model="form[field.key]"
        :is="field.component || ElInput"
        v-bind="field.componentProps"
      >
        <component
          v-for="opt in field.childComponentProps?.options || []"
          :is="field.childComponent"
          :key="opt.value"
          :value="opt.value"
          :label="opt.label"
        />
      </component>
    </component>

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
