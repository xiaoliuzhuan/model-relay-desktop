<script setup lang="ts">
type ConfigGroupStats = {
  total: number;
  openai: number;
  anthropic: number;
};

type ConfigGroupSummary = {
  name: string;
  protocol: string;
  apiUrl: string;
  modelId: string;
};

const props = defineProps<{
  stats: ConfigGroupStats;
  summary: ConfigGroupSummary;
}>();

const overviewCards = computed(() => [
  { label: "配置组总数", value: props.stats.total },
  { label: "OpenAI 组", value: props.stats.openai },
  { label: "Anthropic 组", value: props.stats.anthropic },
  { label: "当前选中", value: props.summary.name, breakAll: true },
]);
</script>

<template>
  <div class="mt-4 mtga-panel-card">
    <div class="grid gap-3 sm:grid-cols-4">
      <div v-for="card in overviewCards" :key="card.label" class="rounded-xl bg-slate-50 px-4 py-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">{{ card.label }}</p>
        <p class="mt-1 text-sm text-slate-900" :class="{ 'break-all': card.breakAll }">
          {{ card.value }}
        </p>
      </div>
    </div>

    <div class="mt-3 grid gap-3 sm:grid-cols-3">
      <div class="rounded-xl border border-slate-200/80 bg-white px-4 py-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">当前协议</p>
        <p class="mt-1 text-sm text-slate-900">{{ summary.protocol }}</p>
      </div>
      <div class="rounded-xl border border-slate-200/80 bg-white px-4 py-3 sm:col-span-2">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">当前 API URL / 模型</p>
        <p class="mt-1 break-all text-sm text-slate-900">
          {{ summary.apiUrl }} · {{ summary.modelId }}
        </p>
      </div>
    </div>
  </div>
</template>
