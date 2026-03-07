<script setup lang="ts">
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
const snapshot = useMtgaSnapshot();
const appInfo = store.appInfo;

const clearConfirmOpen = ref(false);
const clearConfirmTitle = "确认清除数据";
const clearConfirmMessage =
  "确定要清除用户数据吗？该操作将删除配置文件、SSL 证书和 hosts 备份（历史 backups 保留）。";
const themeDialogOpen = ref(false);

const themeConfig = reactive<ThemeConfig>({ ...DEFAULT_THEME_CONFIG });
if (import.meta.client && !snapshot.value.enabled) {
  const savedTheme = loadThemeFromStorage();
  if (savedTheme) {
    copyThemeConfig(themeConfig, savedTheme);
  }
}

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

const backupTooltip = [
  "创建带时间戳的完整数据备份",
  "备份内容：配置文件、SSL证书、hosts备份",
  "备份位置：用户数据目录/backups/backup_时间戳/",
].join("\n");

const restoreTooltip = [
  "从最新备份恢复用户数据（覆盖现有数据）",
  "自动选择最新时间戳的备份进行还原",
  "注意：此操作会覆盖当前的配置和证书",
].join("\n");

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

const handleOpen = () => {
  store.runUserDataOpenDir();
};

const handleBackup = () => {
  store.runUserDataBackup();
};

const handleRestore = () => {
  store.runUserDataRestoreLatest();
};

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
  <div class="flex items-start justify-between gap-3">
    <div>
      <h2 class="mtga-card-title">应用设置</h2>
      <p class="mtga-card-subtitle">管理数据与系统配置</p>
    </div>
    <span class="mtga-chip shrink-0">系统</span>
  </div>

  <div class="mt-5 space-y-4">
    <div class="mtga-panel-banner">
      <p class="font-medium text-slate-900">本页维护本地状态</p>
      <p class="mt-1 text-slate-600">
        用户数据操作会影响当前设备的配置与备份；主题配置只调整界面外观，不改变代理协议和运行流程。
      </p>
    </div>

    <SettingsUserDataSection
      :user-data-mode-label="userDataModeLabel"
      :resolved-user-data-dir="resolvedUserDataDir"
      :default-user-data-dir="defaultUserDataDir"
      :open-dir-tooltip="openDirTooltip"
      :backup-tooltip="backupTooltip"
      :restore-tooltip="restoreTooltip"
      :clear-tooltip="clearTooltip"
      @open="handleOpen"
      @backup="handleBackup"
      @restore="handleRestore"
      @clear="handleClear"
    />

    <SettingsThemeSection
      :theme-config="themeConfig"
      :theme-summary-ready="themeSummaryReady"
      :theme-override-count="themeOverrideCount"
      :theme-status-label="themeStatusLabel"
      @edit="openThemeDialog"
    />
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
