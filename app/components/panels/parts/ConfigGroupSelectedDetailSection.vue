<script setup lang="ts">
type ConfigGroupSummary = {
  name: string;
  protocol: string;
  apiUrl: string;
  modelId: string;
};

const props = defineProps<{
  hasSelection: boolean;
  summary: ConfigGroupSummary;
  apiKeyDisplay: string;
  middleRouteLabel: string;
}>();

const detailRows = computed(() => [
  { label: "配置组名称", value: props.summary.name },
  { label: "上游协议", value: props.summary.protocol },
  { label: "API URL", value: props.summary.apiUrl },
  { label: "模型 ID", value: props.summary.modelId },
  { label: "API Key", value: props.apiKeyDisplay },
  { label: "中转路径", value: props.middleRouteLabel },
]);
</script>

<template>
  <div class="mtga-panel-card">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-medium text-slate-900">当前选中配置组</p>
        <p class="mt-1 text-xs text-slate-600">这里汇总当前真正生效的上游参数，方便快速确认</p>
      </div>
      <span
        class="inline-flex shrink-0 items-center rounded-full px-3 py-1 text-xs"
        :class="hasSelection ? 'bg-indigo-50 text-indigo-700' : 'bg-slate-100 text-slate-500'"
      >
        {{ hasSelection ? "已选择" : "等待选择" }}
      </span>
    </div>

    <div class="mt-4 space-y-2">
      <div
        v-for="row in detailRows"
        :key="row.label"
        class="flex items-start justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3"
      >
        <span class="text-xs text-slate-500">{{ row.label }}</span>
        <span class="break-all text-right text-sm text-slate-900">
          {{ row.value }}
        </span>
      </div>
    </div>

    <div
      class="mt-4 rounded-xl border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-slate-700"
    >
      切换配置组时会先保存当前索引，再热应用选中的协议与路由，减少多协议共存时的误读。
    </div>
  </div>
</template>
