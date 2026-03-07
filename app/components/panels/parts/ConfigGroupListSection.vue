<script setup lang="ts">
type ConfigGroupListItem = {
  index: number;
  title: string;
  displayName: string;
  selectionBadgeLabel: string;
  selectionBadgeClass: string;
  protocolText: string;
  protocolBadgeLabel: string;
  protocolBadgeClass: string;
  middleRoute: string;
  apiUrl: string;
  modelId: string;
  apiKeyDisplay: string;
  selectionHintLabel: string;
  selectionHintClass: string;
};

defineProps<{
  items: ConfigGroupListItem[];
  refreshTooltip: string;
}>();

const emit = defineEmits<{
  refresh: [];
  select: [index: number];
}>();
</script>

<template>
  <div class="mtga-panel-card">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-medium text-slate-900">配置组列表</p>
        <p class="mt-1 text-xs text-slate-600">
          点击卡片即可切换当前生效的上游协议、模型路由与鉴权组合
        </p>
      </div>
      <button
        class="btn btn-xs btn-outline rounded-lg border-slate-200 px-3 text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 tooltip mtga-tooltip"
        :data-tip="refreshTooltip"
        style="--mtga-tooltip-max: 250px"
        @click="emit('refresh')"
      >
        刷新列表
      </button>
    </div>

    <div v-if="items.length" class="mt-4 grid gap-3 lg:grid-cols-2">
      <button
        v-for="item in items"
        :key="item.index"
        type="button"
        class="rounded-2xl border p-4 text-left transition-all duration-150"
        :class="
          item.selectionBadgeLabel === '当前生效'
            ? 'border-indigo-300 bg-indigo-50/80 shadow-[0_10px_30px_-20px_rgba(79,70,229,0.45)]'
            : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-slate-50'
        "
        :title="item.title"
        @click="emit('select', item.index)"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <p class="break-all text-base font-medium text-slate-900">
                {{ item.displayName }}
              </p>
              <span
                class="shrink-0 rounded-full px-2.5 py-1 text-[11px]"
                :class="item.selectionBadgeClass"
              >
                {{ item.selectionBadgeLabel }}
              </span>
            </div>
            <p class="mt-1 break-all text-sm text-slate-600">
              {{ item.protocolText }}
              <span v-if="item.middleRoute"> · {{ item.middleRoute }}</span>
            </p>
          </div>
          <span
            class="shrink-0 rounded-full px-2.5 py-1 text-[11px]"
            :class="item.protocolBadgeClass"
          >
            {{ item.protocolBadgeLabel }}
          </span>
        </div>

        <div class="mt-4 rounded-xl border border-slate-200/80 bg-white/80 p-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">上游参数</p>
          <div class="mt-3 space-y-2">
            <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
              <span class="text-xs text-slate-500">API URL</span>
              <span class="break-all text-right text-sm text-slate-800">
                {{ item.apiUrl }}
              </span>
            </div>
            <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
              <span class="text-xs text-slate-500">模型 ID</span>
              <span class="break-all text-right text-sm text-slate-800">
                {{ item.modelId }}
              </span>
            </div>
            <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
              <span class="text-xs text-slate-500">API Key</span>
              <span class="break-all text-right text-sm text-slate-800">
                {{ item.apiKeyDisplay }}
              </span>
            </div>
          </div>
        </div>

        <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
          <span class="text-xs text-slate-500">切换后会保存并热应用当前配置组</span>
          <span
            class="inline-flex items-center rounded-full px-2 py-1 text-[11px]"
            :class="item.selectionHintClass"
          >
            {{ item.selectionHintLabel }}
          </span>
        </div>
      </button>
    </div>

    <div
      v-else
      class="mt-4 rounded-2xl border border-dashed border-slate-200/80 bg-slate-50/80 px-4 py-8 text-center text-sm text-slate-400"
    >
      暂无配置组
    </div>
  </div>
</template>
