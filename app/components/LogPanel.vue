<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    logs?: string[];
    logText?: string;
    emptyText?: string;
  }>(),
  {
    logs: () => [],
    logText: "",
    emptyText: "日志输出占位",
  },
);

const logBox = ref<HTMLDivElement | null>(null);

const logCount = computed(() => props.logs?.length ?? 0);

const formattedLogs = computed(() => {
  if (props.logText) {
    return props.logText;
  }
  return props.logs && props.logs.length ? props.logs.join("\n") : props.emptyText;
});

const scrollToLatestLog = () => {
  if (!logBox.value) {
    return;
  }

  logBox.value.scrollTop = logBox.value.scrollHeight;

  const outerScroller = logBox.value.closest(".custom-scrollbar");
  if (outerScroller instanceof HTMLElement) {
    outerScroller.scrollTop = outerScroller.scrollHeight;
  }
};

const scheduleScrollToLatestLog = async () => {
  await nextTick();
  requestAnimationFrame(scrollToLatestLog);
};

watch(
  logCount,
  () => {
    void scheduleScrollToLatestLog();
  },
  { flush: "post" },
);

watch(
  formattedLogs,
  () => {
    void scheduleScrollToLatestLog();
  },
  { flush: "post" },
);

onMounted(() => {
  void scheduleScrollToLatestLog();
});
</script>

<template>
  <div class="flex h-full min-h-0 flex-col">
    <div class="flex shrink-0 items-start justify-between gap-3">
      <div>
        <h2 class="mtga-card-title">运行日志</h2>
        <p class="mtga-card-subtitle">实时记录后端与操作状态</p>
      </div>
      <span class="mtga-chip shrink-0">实时输出</span>
    </div>

    <div class="mt-5 shrink-0 mtga-panel-banner">
      <p class="font-medium text-slate-900">运行状态会持续追加到这里</p>
      <p class="mt-1 text-slate-600">
        保持终端式可读性；新日志到达后自动滚动到最新位置，便于快速确认执行结果。
      </p>
    </div>

    <div class="mt-4 flex flex-1 min-h-0 flex-col mtga-panel-card">
      <div class="flex shrink-0 items-start justify-between gap-3">
        <div>
          <p class="text-sm font-medium text-slate-900">日志控制台</p>
          <p class="mt-1 text-xs text-slate-600">
            保留等宽字体与深色背景，让后端输出更容易连续阅读。
          </p>
        </div>
        <span
          class="inline-flex shrink-0 items-center rounded-full border px-3 py-1 text-xs shadow-sm"
          :class="
            logCount > 0
              ? 'border-indigo-100 bg-indigo-50 text-indigo-700'
              : 'border-slate-200 bg-slate-100 text-slate-600'
          "
        >
          {{ logCount > 0 ? `共 ${logCount} 条` : "等待输出" }}
        </span>
      </div>

      <div class="mt-4 mtga-terminal-frame">
        <div
          class="flex shrink-0 items-center justify-between gap-3 border-b border-slate-800/90 px-4 py-2 text-[11px] text-slate-400"
        >
          <div class="flex items-center gap-2" aria-hidden="true">
            <span class="h-2.5 w-2.5 rounded-full bg-rose-400/80" />
            <span class="h-2.5 w-2.5 rounded-full bg-amber-300/80" />
            <span class="h-2.5 w-2.5 rounded-full bg-emerald-400/80" />
          </div>
          <span>{{ logCount > 0 ? "自动跟随最新日志" : "等待新的运行输出" }}</span>
        </div>

        <div ref="logBox" class="flex-1 min-h-0 overflow-auto px-4 py-4">
          <pre
            class="whitespace-pre-wrap text-sm font-mono leading-relaxed"
            :class="logCount > 0 ? 'text-slate-100' : 'text-slate-500'"
            >{{ formattedLogs }}</pre
          >
        </div>
      </div>
    </div>
  </div>
</template>
