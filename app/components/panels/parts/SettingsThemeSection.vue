<script setup lang="ts">
import type { ThemeConfig } from "~/composables/themeConfig";

const props = defineProps<{
  themeConfig: ThemeConfig;
  themeSummaryReady: boolean;
  themeOverrideCount: number;
  themeStatusLabel: string;
}>();

const emit = defineEmits<{
  edit: [];
}>();

const themeStatusClass = computed(() =>
  props.themeSummaryReady && props.themeOverrideCount > 0
    ? "bg-indigo-50 text-indigo-700"
    : "bg-slate-100 text-slate-600",
);

const summaryCards = computed(() => [
  {
    label: "已配置项",
    value: props.themeSummaryReady ? `${props.themeOverrideCount} 项` : "加载中",
  },
  {
    label: "字体",
    value: props.themeSummaryReady ? props.themeConfig.fontFamily || "跟随系统" : "加载中",
    truncate: true,
  },
  {
    label: "背景图",
    value: props.themeSummaryReady
      ? props.themeConfig.backgroundImage
        ? "已设置"
        : "未设置"
      : "加载中",
  },
]);

const colorCards = computed(() => [
  {
    label: "主色",
    value:
      props.themeSummaryReady && props.themeConfig.primaryColor
        ? props.themeConfig.primaryColor
        : "默认",
    swatch:
      props.themeSummaryReady && props.themeConfig.primaryColor
        ? props.themeConfig.primaryColor
        : "var(--color-primary)",
  },
  {
    label: "辅色",
    value:
      props.themeSummaryReady && props.themeConfig.secondaryColor
        ? props.themeConfig.secondaryColor
        : "默认",
    swatch:
      props.themeSummaryReady && props.themeConfig.secondaryColor
        ? props.themeConfig.secondaryColor
        : "var(--mtga-accent-strong)",
  },
  {
    label: "文本",
    value:
      props.themeSummaryReady && props.themeConfig.textPrimaryColor
        ? props.themeConfig.textPrimaryColor
        : "默认",
    swatch:
      props.themeSummaryReady && props.themeConfig.textPrimaryColor
        ? props.themeConfig.textPrimaryColor
        : "var(--mtga-text)",
  },
]);
</script>

<template>
  <div class="mtga-panel-card">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-sm font-medium text-slate-900">主题配置</p>
        <p class="mt-1 text-xs text-slate-600">
          本地保存颜色、字体与背景设置，作为当前桌面界面外观摘要
        </p>
      </div>
      <span
        class="inline-flex shrink-0 items-center rounded-full px-3 py-1 text-xs"
        :class="themeStatusClass"
      >
        {{ themeStatusLabel }}
      </span>
    </div>

    <div class="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(260px,0.9fr)]">
      <div class="rounded-xl border border-slate-200/80 bg-white/80 p-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">当前摘要</p>

        <div class="mt-3 grid gap-2 sm:grid-cols-3">
          <div
            v-for="card in summaryCards"
            :key="card.label"
            class="rounded-lg bg-slate-50 px-3 py-2"
          >
            <p class="text-[11px] uppercase tracking-wide text-slate-400">{{ card.label }}</p>
            <p class="mt-1 text-sm text-slate-900" :class="{ truncate: card.truncate }">
              {{ card.value }}
            </p>
          </div>
        </div>

        <div class="mt-4 grid gap-2 sm:grid-cols-3">
          <div
            v-for="card in colorCards"
            :key="card.label"
            class="rounded-lg border border-slate-200/70 bg-slate-50/80 px-3 py-2"
          >
            <p class="text-[11px] uppercase tracking-wide text-slate-400">{{ card.label }}</p>
            <div class="mt-2 flex items-center gap-2">
              <span
                class="h-3 w-3 rounded-full border border-white shadow-sm"
                :style="{ backgroundColor: card.swatch }"
              />
              <span class="text-sm text-slate-900">
                {{ card.value }}
              </span>
            </div>
          </div>
        </div>

        <div
          class="mt-4 rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-slate-700"
        >
          主题设置仅保存在本地存储，影响当前设备上的界面显示，不会修改代理配置和用户数据内容。
        </div>
      </div>

      <div class="mtga-panel-accent-card">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-sm font-medium text-slate-900">主题编辑</p>
            <p class="mt-1 text-xs text-slate-600">继续使用现有对话框调整颜色、字体与背景资源</p>
          </div>
          <span class="mtga-status-pill-soft"> 外观 </span>
        </div>

        <div
          class="mt-4 space-y-2 rounded-xl border border-white/80 bg-white/70 p-3 text-sm text-slate-700"
        >
          <div class="flex items-center justify-between gap-3">
            <span>颜色变量</span>
            <span class="text-xs text-slate-500">主色 / 辅色 / 状态色</span>
          </div>
          <div class="flex items-center justify-between gap-3">
            <span>排版设置</span>
            <span class="text-xs text-slate-500">字体族与文本色</span>
          </div>
          <div class="flex items-center justify-between gap-3">
            <span>背景资源</span>
            <span class="text-xs text-slate-500">图片地址与视觉氛围</span>
          </div>
        </div>

        <button class="mtga-btn-primary mt-4" @click="emit('edit')">打开主题配置</button>
      </div>
    </div>
  </div>
</template>
