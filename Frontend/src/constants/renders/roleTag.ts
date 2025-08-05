// renderers/roleTag.ts
import { h } from "vue";
import { ElTag } from "element-plus";
import type { User } from "~/types/models/User";

export function renderUserRole(row: User) {
  let tagType:
    | "primary"
    | "success"
    | "warning"
    | "info"
    | "danger"
    | undefined = undefined;
  let label = "";

  switch (row.role) {
    case "teacher":
      tagType = "primary";
      label = "Teacher 👩‍🏫";
      break;
    case "admin":
      tagType = "danger";
      label = "Admin ⚙️";
      break;
    case "student":
      tagType = "success";
      label = "Student 🎓";
      break;
    default:
      tagType = undefined;
      label = row.role;
  }

  return h("div", { style: { display: "flex", justifyContent: "center" } }, [
    tagType
      ? h(ElTag, { type: tagType, effect: "light" }, () => label)
      : h(ElTag, { effect: "light", style: { color: "#999" } }, () => label),
  ]);
}
