<script setup lang="ts">
/**
 * 设置面板组件
 * 提供用户数据管理、备份、还原及清理功能
 */
import {
  type ThemeConfig,
  DEFAULT_THEME_CONFIG,
  applyThemeConfig,
  copyThemeConfig,
  loadThemeFromStorage,
  sanitizeThemeConfig,
  saveThemeToStorage,
} from "~/composables/themeConfig";

const store = useMtgaStore();
const appInfo = store.appInfo;

const clearConfirmOpen = ref(false);
const clearConfirmTitle = "确认清除数据";
const clearConfirmMessage =
  "确定要清除用户数据吗？该操作将删除配置文件、SSL 证书和 hosts 备份（历史 backups 保留）。";
const themeDialogOpen = ref(false);

const themeConfig = reactive<ThemeConfig>({ ...DEFAULT_THEME_CONFIG });
if (import.meta.client) {
  const savedTheme = loadThemeFromStorage();
  if (savedTheme) {
    copyThemeConfig(themeConfig, savedTheme);
  }
}

/**
 * 打开目录的工具提示内容
 */
const openDirTooltip = computed(() => {
  const current = appInfo.value.user_data_dir?.trim();
  const fallback = appInfo.value.default_user_data_dir?.trim();
  if (current && fallback && current !== fallback) {
    return `使用系统文件管理器打开用户数据目录\n当前：${current}\n默认：${fallback}`;
  }
  if (current) {
    return `使用系统文件管理器打开用户数据目录\n目录：${current}`;
  }
  if (fallback) {
    return `使用系统文件管理器打开用户数据目录\n默认目录：${fallback}`;
  }
  return "使用系统文件管理器打开用户数据目录";
});

const currentUserDataDir = computed(() => appInfo.value.user_data_dir?.trim() || "");
const defaultUserDataDir = computed(() => appInfo.value.default_user_data_dir?.trim() || "");
const resolvedUserDataDir = computed(
  () => currentUserDataDir.value || defaultUserDataDir.value || "未获取",
);
const userDataModeLabel = computed(() => {
  if (
    currentUserDataDir.value &&
    defaultUserDataDir.value &&
    currentUserDataDir.value !== defaultUserDataDir.value
  ) {
    return "自定义目录";
  }
  if (currentUserDataDir.value || defaultUserDataDir.value) {
    return "默认目录";
  }
  return "待初始化";
});

/**
 * 备份数据的工具提示内容
 */
const backupTooltip = [
  "创建带时间戳的完整数据备份",
  "备份内容：配置文件、SSL证书、hosts备份",
  "备份位置：用户数据目录/backups/backup_时间戳/",
].join("\n");

/**
 * 还原数据的工具提示内容
 */
const restoreTooltip = [
  "从最新备份恢复用户数据（覆盖现有数据）",
  "自动选择最新时间戳的备份进行还原",
  "注意：此操作会覆盖当前的配置和证书",
].join("\n");

/**
 * 清除数据的工具提示内容
 */
const clearTooltip = [
  "删除所有用户数据（保留历史备份）",
  "清除内容：配置文件、SSL证书、hosts备份",
  "保留内容：backups文件夹及其历史备份",
].join("\n");

const themeSummaryReady = ref(false);

onMounted(() => {
  themeSummaryReady.value = true;
});

const themeOverrideCount = computed(() =>
  themeSummaryReady.value
    ? [
        themeConfig.primaryColor,
        themeConfig.secondaryColor,
        themeConfig.textPrimaryColor,
        themeConfig.textSecondaryColor,
        themeConfig.infoColor,
        themeConfig.warningColor,
        themeConfig.errorColor,
        themeConfig.successColor,
        themeConfig.fontFamily,
        themeConfig.backgroundImage,
      ].filter((value) => value.trim()).length
    : 0,
);

const themeStatusLabel = computed(() => {
  if (!themeSummaryReady.value) {
    return "本地主题";
  }
  return themeOverrideCount.value > 0 ? `已自定义 ${themeOverrideCount.value} 项` : "跟随默认";
});

/**
 * 处理打开数据目录
 */
const handleOpen = () => {
  store.runUserDataOpenDir();
};

/**
 * 处理备份数据
 */
const handleBackup = () => {
  store.runUserDataBackup();
};

/**
 * 处理还原数据
 */
const handleRestore = () => {
  store.runUserDataRestoreLatest();
};

/**
 * 处理清除数据
 */
const handleClear = () => {
  clearConfirmOpen.value = true;
};

const cancelClear = () => {
  clearConfirmOpen.value = false;
};

const confirmClear = () => {
  clearConfirmOpen.value = false;
  store.runUserDataClear();
};

const openThemeDialog = () => {
  themeDialogOpen.value = true;
};

const handleThemeSave = (value: ThemeConfig) => {
  const normalized = sanitizeThemeConfig(value);
  copyThemeConfig(themeConfig, normalized);
  applyThemeConfig(themeConfig);
  const saveResult = saveThemeToStorage(themeConfig);
  if (saveResult.ok) {
    store.appendLog("主题配置已保存");
    return;
  }
  store.appendLog(`主题配置已应用，但本地保存失败：${saveResult.error}`);
};
</script>

<template>
  <div class="flex items-center justify-between gap-3">
    <div>
      <h2 class="mtga-card-title">应用设置</h2>
      <p class="mtga-card-subtitle">管理数据与系统配置</p>
    </div>
    <span class="mtga-chip">系统</span>
  </div>

  <div class="mt-5 space-y-4">
    <div
      class="rounded-2xl border border-indigo-100 bg-gradient-to-r from-white via-sky-50 to-indigo-50 px-4 py-3 text-sm text-slate-700 shadow-sm"
    >
      <p class="font-medium text-slate-900">本页维护本地状态</p>
      <p class="mt-1 text-slate-600">
        用户数据操作会影响当前设备的配置与备份；主题配置只调整界面外观，不改变代理协议和运行流程。
      </p>
    </div>

    <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-medium text-slate-900">用户数据</p>
          <p class="mt-1 text-xs text-slate-600">目录位置、备份范围与恢复入口都在这里集中处理</p>
        </div>
        <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs text-indigo-700">
          {{ userDataModeLabel }}
        </span>
      </div>

      <div class="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
        <div class="rounded-xl border border-slate-200/80 bg-white/80 p-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">目录与保留策略</p>
          <div class="mt-3 space-y-2">
            <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
              <span class="text-xs text-slate-500">当前目录</span>
              <span class="break-all text-right text-sm text-slate-900">{{
                resolvedUserDataDir
              }}</span>
            </div>
            <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
              <span class="text-xs text-slate-500">默认目录</span>
              <span class="break-all text-right text-sm text-slate-900">
                {{ defaultUserDataDir || "未获取" }}
              </span>
            </div>
            <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
              <span class="text-xs text-slate-500">备份策略</span>
              <span class="text-right text-sm text-slate-900"
                >完整备份至 backups/ 目录，清除时保留历史备份</span
              >
            </div>
          </div>

          <div
            class="mt-4 rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-slate-700"
          >
            备份、还原与清除都作用于当前用户数据目录；如目录被重定向，这里展示的是最终实际位置。
          </div>
        </div>

        <div
          class="rounded-xl border border-indigo-100 bg-gradient-to-br from-white via-indigo-50 to-sky-50 p-4"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-medium text-slate-900">主要操作</p>
              <p class="mt-1 text-xs text-slate-600">
                保留现有四个动作，用更清晰的主操作区统一展示
              </p>
            </div>
            <span
              class="rounded-full bg-white/80 px-2.5 py-1 text-[11px] text-indigo-700 shadow-sm"
            >
              执行区
            </span>
          </div>

          <div class="mt-4 grid gap-2 sm:grid-cols-2">
            <button
              class="mtga-btn-outline tooltip mtga-tooltip"
              :data-tip="openDirTooltip"
              @click="handleOpen"
            >
              打开目录
            </button>
            <button
              class="mtga-btn-primary tooltip mtga-tooltip"
              :data-tip="backupTooltip"
              style="--mtga-tooltip-max: 360px"
              @click="handleBackup"
            >
              备份数据
            </button>
            <button
              class="mtga-btn-outline tooltip mtga-tooltip"
              :data-tip="restoreTooltip"
              style="--mtga-tooltip-max: 360px"
              @click="handleRestore"
            >
              还原数据
            </button>
            <button
              class="mtga-btn-error tooltip mtga-tooltip"
              :data-tip="clearTooltip"
              style="--mtga-tooltip-max: 360px"
              @click="handleClear"
            >
              清除数据
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-medium text-slate-900">主题配置</p>
          <p class="mt-1 text-xs text-slate-600">
            本地保存颜色、字体与背景设置，作为当前桌面界面外观摘要
          </p>
        </div>
        <span
          class="rounded-full px-3 py-1 text-xs"
          :class="
            themeSummaryReady && themeOverrideCount > 0
              ? 'bg-indigo-50 text-indigo-700'
              : 'bg-slate-100 text-slate-600'
          "
        >
          {{ themeStatusLabel }}
        </span>
      </div>

      <div class="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(260px,0.9fr)]">
        <div class="rounded-xl border border-slate-200/80 bg-white/80 p-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">当前摘要</p>

          <div class="mt-3 grid gap-2 sm:grid-cols-3">
            <div class="rounded-lg bg-slate-50 px-3 py-2">
              <p class="text-[11px] uppercase tracking-wide text-slate-400">已配置项</p>
              <p class="mt-1 text-sm text-slate-900">
                {{ themeSummaryReady ? `${themeOverrideCount} 项` : "加载中" }}
              </p>
            </div>
            <div class="rounded-lg bg-slate-50 px-3 py-2">
              <p class="text-[11px] uppercase tracking-wide text-slate-400">字体</p>
              <p class="mt-1 truncate text-sm text-slate-900">
                {{ themeSummaryReady ? themeConfig.fontFamily || "跟随系统" : "加载中" }}
              </p>
            </div>
            <div class="rounded-lg bg-slate-50 px-3 py-2">
              <p class="text-[11px] uppercase tracking-wide text-slate-400">背景图</p>
              <p class="mt-1 text-sm text-slate-900">
                {{
                  themeSummaryReady ? (themeConfig.backgroundImage ? "已设置" : "未设置") : "加载中"
                }}
              </p>
            </div>
          </div>

          <div class="mt-4 grid gap-2 sm:grid-cols-3">
            <div class="rounded-lg border border-slate-200/70 bg-slate-50/80 px-3 py-2">
              <p class="text-[11px] uppercase tracking-wide text-slate-400">主色</p>
              <div class="mt-2 flex items-center gap-2">
                <span
                  class="h-3 w-3 rounded-full border border-white shadow-sm"
                  :style="{
                    backgroundColor:
                      themeSummaryReady && themeConfig.primaryColor
                        ? themeConfig.primaryColor
                        : 'var(--color-primary)',
                  }"
                />
                <span class="text-sm text-slate-900">
                  {{
                    themeSummaryReady && themeConfig.primaryColor
                      ? themeConfig.primaryColor
                      : "默认"
                  }}
                </span>
              </div>
            </div>
            <div class="rounded-lg border border-slate-200/70 bg-slate-50/80 px-3 py-2">
              <p class="text-[11px] uppercase tracking-wide text-slate-400">辅色</p>
              <div class="mt-2 flex items-center gap-2">
                <span
                  class="h-3 w-3 rounded-full border border-white shadow-sm"
                  :style="{
                    backgroundColor:
                      themeSummaryReady && themeConfig.secondaryColor
                        ? themeConfig.secondaryColor
                        : 'var(--mtga-accent-strong)',
                  }"
                />
                <span class="text-sm text-slate-900">
                  {{
                    themeSummaryReady && themeConfig.secondaryColor
                      ? themeConfig.secondaryColor
                      : "默认"
                  }}
                </span>
              </div>
            </div>
            <div class="rounded-lg border border-slate-200/70 bg-slate-50/80 px-3 py-2">
              <p class="text-[11px] uppercase tracking-wide text-slate-400">文本</p>
              <div class="mt-2 flex items-center gap-2">
                <span
                  class="h-3 w-3 rounded-full border border-white shadow-sm"
                  :style="{
                    backgroundColor:
                      themeSummaryReady && themeConfig.textPrimaryColor
                        ? themeConfig.textPrimaryColor
                        : 'var(--mtga-text)',
                  }"
                />
                <span class="text-sm text-slate-900">
                  {{
                    themeSummaryReady && themeConfig.textPrimaryColor
                      ? themeConfig.textPrimaryColor
                      : "默认"
                  }}
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

        <div
          class="rounded-xl border border-indigo-100 bg-gradient-to-br from-white via-indigo-50 to-sky-50 p-4"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-medium text-slate-900">主题编辑</p>
              <p class="mt-1 text-xs text-slate-600">继续使用现有对话框调整颜色、字体与背景资源</p>
            </div>
            <span
              class="rounded-full bg-white/80 px-2.5 py-1 text-[11px] text-indigo-700 shadow-sm"
            >
              外观
            </span>
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

          <button class="mtga-btn-primary mt-4" @click="openThemeDialog">打开主题配置</button>
        </div>
      </div>
    </div>
  </div>

  <ConfirmDialog
    :open="clearConfirmOpen"
    :title="clearConfirmTitle"
    :message="clearConfirmMessage"
    confirm-text="确认清除"
    type="error"
    @cancel="cancelClear"
    @confirm="confirmClear"
  />

  <ThemeSettingsDialog
    v-model:open="themeDialogOpen"
    :config="themeConfig"
    @save="handleThemeSave"
  />
</template>
