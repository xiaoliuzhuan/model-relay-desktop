<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    logs?: string[];
    emptyText?: string;
  }>(),
  {
    logs: () => [],
    emptyText: "日志输出占位",
  },
);

const logBox = ref<HTMLDivElement | null>(null);

const logCount = computed(() => props.logs?.length ?? 0);

const formattedLogs = computed(() =>
  props.logs && props.logs.length ? props.logs.join("\n") : props.emptyText,
);

const scrollToLatestLog = () => {
  if (!logBox.value) {
    return;
  }
  logBox.value.scrollTop = logBox.value.scrollHeight;
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
  <div class="flex items-center justify-between gap-3 shrink-0">
    <div>
      <h2 class="mtga-card-title">运行日志</h2>
      <p class="mtga-card-subtitle">实时记录后端与操作状态</p>
    </div>
    <div class="flex items-center gap-2">
      <span class="mtga-chip">实时输出</span>
      <span class="text-xs text-slate-500">共 {{ logCount }} 条</span>
    </div>
  </div>
  <div
    ref="logBox"
    class="mt-4 flex-1 overflow-auto rounded-xl border border-indigo-200/70 bg-slate-900/[0.94] p-4 text-sm font-mono text-slate-100 shadow-inner shadow-indigo-900/20"
  >
    <pre class="whitespace-pre-wrap leading-relaxed">{{ formattedLogs }}</pre>
  </div>
</template>
