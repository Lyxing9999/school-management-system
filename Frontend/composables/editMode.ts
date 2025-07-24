// editMode.ts
import type { InjectionKey, Ref } from "vue";

export const EditModeKey: InjectionKey<Ref<boolean>> = Symbol("EditMode");
