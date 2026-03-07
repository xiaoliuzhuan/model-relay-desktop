<script setup lang="ts">
const props = defineProps<{
  userDataModeLabel: string;
  resolvedUserDataDir: string;
  defaultUserDataDir: string;
  openDirTooltip: string;
  backupTooltip: string;
  restoreTooltip: string;
  clearTooltip: string;
}>();

const emit = defineEmits<{
  open: [];
  backup: [];
  restore: [];
  clear: [];
}>();

const directoryRows = computed(() => [
  { label: "当前目录", value: props.resolvedUserDataDir, valueClass: "break-all" },
  { label: "默认目录", value: props.defaultUserDataDir || "未获取", valueClass: "break-all" },
  {
    label: "备份策略",
    value: "完整备份至 backups/ 目录，清除时保留历史备份",
    valueClass: "break-words",
  },
]);
</script>

<template>
  <div class="mtga-panel-card">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-medium text-slate-900">用户数据</p>
        <p class="mt-1 text-xs text-slate-600">目录位置、备份范围与恢复入口都在这里集中处理</p>
      </div>
      <span class="mtga-status-pill">
        {{ userDataModeLabel }}
      </span>
    </div>

    <div class="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
      <div class="rounded-xl border border-slate-200/80 bg-white/80 p-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">目录与保留策略</p>
        <div class="mt-3 space-y-2">
          <div
            v-for="row in directoryRows"
            :key="row.label"
            class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2"
          >
            <span class="text-xs text-slate-500">{{ row.label }}</span>
            <span class="text-right text-sm text-slate-900" :class="row.valueClass">
              {{ row.value }}
            </span>
          </div>
        </div>

        <div
          class="mt-4 rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-slate-700"
        >
          备份、还原与清除都作用于当前用户数据目录；如目录被重定向，这里展示的是最终实际位置。
        </div>
      </div>

      <div class="mtga-panel-accent-card">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-sm font-medium text-slate-900">主要操作</p>
            <p class="mt-1 text-xs text-slate-600">保留现有四个动作，用更清晰的主操作区统一展示</p>
          </div>
          <span class="mtga-status-pill-soft"> 执行区 </span>
        </div>

        <div class="mt-4 grid gap-2 sm:grid-cols-2">
          <button
            class="mtga-btn-outline tooltip mtga-tooltip"
            :data-tip="openDirTooltip"
            @click="emit('open')"
          >
            打开目录
          </button>
          <button
            class="mtga-btn-primary tooltip mtga-tooltip"
            :data-tip="backupTooltip"
            style="--mtga-tooltip-max: 360px"
            @click="emit('backup')"
          >
            备份数据
          </button>
          <button
            class="mtga-btn-outline tooltip mtga-tooltip"
            :data-tip="restoreTooltip"
            style="--mtga-tooltip-max: 360px"
            @click="emit('restore')"
          >
            还原数据
          </button>
          <button
            class="mtga-btn-error tooltip mtga-tooltip"
            :data-tip="clearTooltip"
            style="--mtga-tooltip-max: 360px"
            @click="emit('clear')"
          >
            清除数据
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
