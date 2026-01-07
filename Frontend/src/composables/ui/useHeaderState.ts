import { computed } from "vue";

/**
 * This matches the 'stats' item type expected by <OverviewHeader />
 */
export type HeaderStat = {
  key?: string | number;
  value: number;
  singular?: string;
  plural?: string;
  label?: string;
  suffix?: string;
  prefix?: string;
  variant?: "primary" | "secondary";
  dotClass?: string;
};

/**
 * Config for building one stat item.
 * - getValue: function so it works nicely with computed/refs.
 * - label: optional function when you want a custom text (e.g. "Present rate: 95%").
 */
export type HeaderStatConfig = {
  key?: string | number;
  getValue: () => number;
  singular?: string;
  plural?: string;
  label?: (value: number) => string | undefined;
  suffix?: string;
  prefix?: string;
  variant?: "primary" | "secondary";
  dotClass?: string;
  hideWhenZero?: boolean; // common case
};

export function useHeaderState(config: { items: HeaderStatConfig[] }) {
  const headerState = computed<HeaderStat[]>(() => {
    const result: HeaderStat[] = [];

    for (const item of config.items) {
      const value = item.getValue();

      if (item.hideWhenZero && !value) {
        continue;
      }

      const label = item.label ? item.label(value) : undefined;

      result.push({
        key: item.key,
        value,
        singular: item.singular,
        plural: item.plural,
        label,
        suffix: item.suffix,
        prefix: item.prefix,
        variant: item.variant,
        dotClass: item.dotClass,
      });
    }

    return result;
  });

  return { headerState };
}
