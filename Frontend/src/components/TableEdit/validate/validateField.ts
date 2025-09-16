import type { Rule } from "~/components/types/tableEdit";

export function validateField(value: any, rules: Rule[] = []): string | null {
  for (const rule of rules) {
    if (rule.required && (value === undefined || value === "")) {
      return rule.message;
    }
    if (rule.min && String(value).length < rule.min) {
      return rule.message;
    }
    if (rule.max && String(value).length > rule.max) {
      return rule.message;
    }
    if (rule.pattern && !rule.pattern.test(value)) {
      return rule.message;
    }
    if (rule.validator) {
      let error: string | null = null;
      rule.validator(rule, value, (err?: Error) => {
        if (err) error = err.message;
      });
      if (error) return error;
    }
  }
  return null;
}
