<script setup lang="ts">
import { computed } from "vue";

interface FooterLink {
  name: string;
  url: string;
  external?: boolean;
}

interface Props {
  organizationName?: string;
  links?: FooterLink[];
  version?: string;
  showVersion?: boolean;
  visible?: boolean;
  compact?: boolean;
  autoHideOnMobile?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  organizationName: "HRMS",
  links: () => [
    { name: "Privacy Policy", url: "#" },
    { name: "Terms of Service", url: "#" },
  ],
  version: "v1.0.0",
  showVersion: true,
  visible: true,
  compact: true,
  autoHideOnMobile: false,
});

const currentYear = computed(() => new Date().getFullYear());

const footerClasses = computed(() => ({
  "app-footer": true,
  "footer-compact": props.compact,
  "footer-hidden-mobile": props.autoHideOnMobile,
}));

const copyrightText = computed(
  () =>
    `© ${currentYear.value} ${props.organizationName}. All rights reserved.`,
);
</script>

<template>
  <footer v-if="props.visible" :class="footerClasses" role="contentinfo">
    <div class="footer-content">
      <p class="copyright">{{ copyrightText }}</p>

      <nav class="footer-links" aria-label="Footer navigation">
        <a
          v-for="link in props.links"
          :key="link.name"
          :href="link.url"
          class="footer-link"
          :target="link.external ? '_blank' : undefined"
          :rel="link.external ? 'noopener noreferrer' : undefined"
        >
          {{ link.name }}
        </a>
      </nav>

      <span
        v-if="props.showVersion"
        class="footer-version"
        aria-label="Application version"
      >
        {{ props.version }}
      </span>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  padding: 0.5rem 0.75rem;
  font-size: 0.78rem;
  color: var(--muted-color, rgba(255, 255, 255, 0.72));
  border-top: 1px solid var(--footer-border, rgba(255, 255, 255, 0.08));
  background-color: var(--footer-bg, transparent);
}
.footer-content {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  flex-wrap: wrap;
  white-space: nowrap;
}
.footer-content > * {
  margin: 0;
}
.footer-links {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
}
.footer-link {
  color: var(--text-color, inherit);
  text-decoration: none;
  opacity: 0.85;
}
.footer-link:hover {
  opacity: 1;
}
.footer-version {
  color: var(--muted-color, rgba(255, 255, 255, 0.55));
}
.footer-compact {
  padding: 0.35rem 0.5rem;
  font-size: 0.74rem;
}
.footer-hidden-mobile {
  display: block;
}
@media (max-width: 640px) {
  .footer-hidden-mobile {
    display: none;
  }
}
</style>
