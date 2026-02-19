<script setup lang="ts">
import DOMPurify from "dompurify";
import { isTauriRuntime } from "../../composables/runtime";

/**
 * 更新提示对话框
 */
const props = withDefaults(
  defineProps<{
    open?: boolean;
    versionLabel?: string;
    notesHtml?: string;
    releaseUrl?: string;
  }>(),
  {
    open: false,
    versionLabel: "",
    notesHtml: "",
    releaseUrl: "",
  },
);

const emit = defineEmits<{
  (event: "update:open", value: boolean): void;
  (event: "close"): void;
  (event: "open-release"): void;
}>();

const openModel = computed({
  get: () => props.open,
  set: (value: boolean) => emit("update:open", value),
});

const sanitizedNotesHtml = computed(() => {
  const source = props.notesHtml?.trim() ?? "";
  if (!source) {
    return "";
  }
  const sanitized = DOMPurify.sanitize(source, { WHOLE_DOCUMENT: true });
  if (!sanitized) {
    return "";
  }
  if (typeof window === "undefined") {
    return sanitized;
  }
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(sanitized, "text/html");
    const tauriRuntime = isTauriRuntime();
    doc.querySelectorAll("a[href]").forEach((anchor) => {
      if (tauriRuntime) {
        anchor.removeAttribute("target");
        anchor.removeAttribute("rel");
        return;
      }
      anchor.setAttribute("target", "_blank");
      anchor.setAttribute("rel", "noopener noreferrer");
    });
    const bodyHtml = doc.body?.innerHTML?.trim() ?? "";
    return bodyHtml || sanitized;
  } catch {
    return sanitized;
  }
});

const resolveExternalUrl = (href: string) => {
  const trimmed = href.trim();
  if (!trimmed) {
    return "";
  }
  if (/^https?:\/\//i.test(trimmed)) {
    return trimmed;
  }
  if (!props.releaseUrl) {
    return trimmed;
  }
  try {
    return new URL(trimmed, props.releaseUrl).toString();
  } catch {
    return trimmed;
  }
};

const openExternalUrl = async (href: string) => {
  const url = resolveExternalUrl(href);
  if (!url || typeof window === "undefined") {
    return;
  }
  if (isTauriRuntime()) {
    try {
      const { open } = await import("@tauri-apps/plugin-shell");
      await open(url);
      return;
    } catch (error) {
      console.warn("[mtga] open notes link failed", error);
      return;
    }
  }
  const opened = window.open(url, "_blank", "noopener,noreferrer");
  if (!opened) {
    window.location.href = url;
  }
};

const handleNotesClick = async (event: MouseEvent) => {
  const eventTarget = event.target;
  if (!(eventTarget instanceof HTMLElement)) {
    return;
  }
  const anchor = eventTarget.closest("a");
  if (!(anchor instanceof HTMLAnchorElement)) {
    return;
  }
  const href = anchor.getAttribute("href") ?? "";
  if (!href) {
    return;
  }
  event.preventDefault();
  await openExternalUrl(href);
};

const handleDialogClose = () => {
  emit("close");
};

const handleOpenRelease = () => {
  emit("open-release");
};
</script>

<template>
  <MtgaDialog v-model:open="openModel" max-width="max-w-md" @close="handleDialogClose">
    <template #header>
      <div class="flex items-center justify-between bg-white/50">
        <h3 class="mtga-card-title text-lg!">发现新版本</h3>
        <div
          v-if="props.versionLabel"
          class="mtga-chip bg-amber-50 border-amber-200! text-amber-700 font-medium"
        >
          {{ props.versionLabel }}
        </div>
      </div>
    </template>

    <div class="px-6 py-4">
      <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">更新日志</div>
      <div
        class="mtga-soft-panel bg-slate-50/40 max-h-[260px] overflow-y-auto p-4 custom-scrollbar"
        @click="handleNotesClick"
      >
        <!-- eslint-disable vue/no-v-html -->
        <div
          v-if="sanitizedNotesHtml"
          class="text-sm text-slate-600 leading-relaxed wrap-break-word space-y-2 [&_ul]:list-disc [&_ul]:pl-5 [&_li]:mt-1 [&_a]:text-amber-600 [&_a]:underline [&_a]:underline-offset-2 [&_a:hover]:text-amber-700"
          v-html="sanitizedNotesHtml"
        />
        <!-- eslint-enable vue/no-v-html -->
        <div v-else class="text-sm text-slate-400 italic py-6 text-center">
          该版本暂无更新说明。
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-center w-full">
        <button
          class="mtga-btn-dialog-primary w-full max-w-xs"
          :disabled="!props.releaseUrl"
          @click="handleOpenRelease"
        >
          前往发布页
        </button>
      </div>
    </template>
  </MtgaDialog>
</template>
