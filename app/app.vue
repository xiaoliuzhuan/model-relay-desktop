<script setup lang="ts">
import { ICONS } from "./composables/icons";
import { applyThemeConfig, loadThemeFromStorage } from "./composables/themeConfig";

const {
  logs,
  init,
  appInfo,
  hasNewVersion,
  updateDialogOpen,
  updateVersionLabel,
  updateNotesHtml,
  updateReleaseUrl,
  runCheckUpdates,
  runCheckUpdatesOnce,
  closeUpdateDialog,
  openUpdateRelease,
  stopLogStream,
  stopProxyStepListener,
  panelNavTarget,
  panelNavSignal,
  runProxyStartAll,
} = useMtgaStore();

if (import.meta.client) {
  const savedTheme = loadThemeFromStorage();
  if (savedTheme) {
    applyThemeConfig(savedTheme);
  }
}

/**
 * 当前选中的左侧面板 ID
 */
const activeTab = ref("config-group");
const direction = ref<"down" | "up">("down");

/**
 * 处理导航切换
 * @param id 目标面板 ID
 */
const selectTab = (id: string) => {
  const oldIndex = navigation.findIndex((item) => item.id === activeTab.value);
  const newIndex = navigation.findIndex((item) => item.id === id);

  if (newIndex !== oldIndex) {
    direction.value = newIndex > oldIndex ? "down" : "up";
    activeTab.value = id;
  }
};

const handleStartAll = () => {
  selectTab("run-logs");
  runProxyStartAll();
};

/**
 * 全局 Tooltip 代理状态
 */
const tooltipProxy = reactive({
  show: false,
  content: "",
  maxWidth: "280px",
  style: {} as Record<string, string>,
});

// 检测是否支持 CSS 锚点定位 API (macOS WebKit 目前不支持)
const supportsAnchor =
  typeof CSS !== "undefined" && CSS.supports && CSS.supports("anchor-name", "--test");

// 记录当前激活了锚点的元素，用于及时清理
let lastAnchorTarget: HTMLElement | null = null;

/**
 * 监听全局鼠标悬停，捕获 mtga-tooltip 元素
 */
const handleGlobalMouseOver = (e: MouseEvent) => {
  const eventTarget = e.target;
  const target = eventTarget instanceof HTMLElement ? eventTarget.closest(".mtga-tooltip") : null;

  if (target instanceof HTMLElement) {
    // 如果目标换了，先清理旧目标的锚点
    if (lastAnchorTarget && lastAnchorTarget !== target) {
      lastAnchorTarget.style.removeProperty("anchor-name");
    }

    tooltipProxy.content = target.getAttribute("data-tip") || "";
    tooltipProxy.maxWidth = target.style.getPropertyValue("--mtga-tooltip-max") || "280px";
    tooltipProxy.show = true;

    if (supportsAnchor) {
      // 支持锚点定位：给新目标设置锚点名称
      target.style.setProperty("anchor-name", "--mtga-tooltip-anchor");
      tooltipProxy.style = {};
    } else {
      // 不支持锚点定位 (如 macOS)：手动计算位置
      const rect = target.getBoundingClientRect();
      tooltipProxy.style = {
        left: `${rect.left + rect.width / 2}px`,
        bottom: `${window.innerHeight - rect.top + 10}px`,
        top: "auto",
      };
    }

    lastAnchorTarget = target;
  } else {
    tooltipProxy.show = false;
    // 离开 tooltip 区域时清理锚点
    if (lastAnchorTarget) {
      lastAnchorTarget.style.removeProperty("anchor-name");
      lastAnchorTarget = null;
    }
  }
};

/**
 * 导航菜单配置
 */
const navigation = [
  { id: "config-group", name: "代理配置组", icon: ICONS.CONFIG_GROUP },
  { id: "global-config", name: "全局配置", icon: ICONS.GLOBAL_CONFIG },
  { id: "main-tabs", name: "主要流程", icon: ICONS.MAIN_TABS },
  { id: "run-logs", name: "运行日志", icon: ICONS.RUN_LOGS },
  { id: "settings", name: "设置", icon: ICONS.SETTINGS },
];

const resolvePanelTarget = (value: string | null) => {
  if (!value) {
    return null;
  }
  return navigation.some((item) => item.id === value) ? value : null;
};

watch(
  panelNavSignal,
  () => {
    const resolved = resolvePanelTarget(panelNavTarget.value);
    if (!resolved) {
      return;
    }
    selectTab(resolved);
  },
  { immediate: true },
);

onMounted(async () => {
  await init();
  await runCheckUpdatesOnce();
});

onBeforeUnmount(() => {
  stopLogStream();
  stopProxyStepListener();
});
</script>

<template>
  <div @mouseover="handleGlobalMouseOver">
    <AppShell :right-hidden="true">
      <template #left>
        <div class="flex items-stretch h-full min-h-0">
          <!-- 垂直菜单栏 -->
          <div class="w-38 border-r border-indigo-100/80 flex flex-col bg-white/45 p-3 shrink-0">
            <ul class="menu p-0 gap-1">
              <li v-for="item in navigation" :key="item.id">
                <a
                  :class="[
                    'group flex flex-row items-center justify-start gap-2 px-2.5 py-2 rounded-lg border transition-all duration-200',
                    activeTab === item.id
                      ? 'border-indigo-300/60 bg-indigo-500/12 text-indigo-700'
                      : 'border-transparent text-slate-500 hover:bg-indigo-50/70 hover:text-slate-700',
                  ]"
                  @click="selectTab(item.id)"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-[18px] w-[18px] opacity-85 shrink-0"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="1.8"
                      :d="item.icon"
                    />
                  </svg>
                  <span class="truncate text-sm font-semibold tracking-[0.01em]">{{
                    item.name
                  }}</span>
                </a>
              </li>
            </ul>

            <!-- 关于与更新 -->
            <div class="mt-auto pt-4 border-t border-slate-200/50 flex flex-col gap-2 px-1">
              <div class="flex flex-col gap-0.5">
                <div class="relative w-fit">
                  <div class="text-[11px] font-medium text-slate-400">
                    {{ appInfo.version }}
                  </div>
                  <span v-if="hasNewVersion" class="mtga-badge-new -top-1.5! -right-9!"> NEW </span>
                </div>
              </div>

              <button
                class="btn btn-xs btn-outline rounded-lg border-slate-200 hover:border-indigo-500 hover:bg-indigo-50 hover:text-indigo-600 font-bold w-full"
                @click="runCheckUpdates"
              >
                检查更新
              </button>

              <div class="text-[10px] text-slate-400/80 text-center mt-1">powered by BiFangKNT</div>
            </div>
          </div>

          <!-- 面板内容区域 -->
          <div class="flex-1 min-w-0 p-6 overflow-hidden flex flex-col">
            <Transition
              enter-active-class="transition duration-200 ease-out"
              :enter-from-class="
                direction === 'down' ? 'translate-y-4 opacity-0' : '-translate-y-4 opacity-0'
              "
              enter-to-class="translate-y-0 opacity-100"
              leave-active-class="transition duration-150 ease-in"
              leave-from-class="translate-y-0 opacity-100"
              :leave-to-class="
                direction === 'down' ? '-translate-y-4 opacity-0' : 'translate-y-4 opacity-0'
              "
              mode="out-in"
            >
              <div
                :key="activeTab"
                class="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar"
              >
                <ConfigGroupPanel v-if="activeTab === 'config-group'" />
                <GlobalConfigPanel v-if="activeTab === 'global-config'" />
                <MainTabs v-if="activeTab === 'main-tabs'" />
                <LogPanel v-if="activeTab === 'run-logs'" :logs="logs" class="h-full" />
                <SettingsPanel v-if="activeTab === 'settings'" />
              </div>
            </Transition>
          </div>
        </div>
      </template>

      <template #footer>
        <FooterActions @start-all="handleStartAll" />
      </template>
    </AppShell>

    <UpdateDialog
      :open="updateDialogOpen"
      :version-label="updateVersionLabel"
      :notes-html="updateNotesHtml"
      :release-url="updateReleaseUrl"
      @close="closeUpdateDialog"
      @open-release="openUpdateRelease"
    />

    <!-- 全局 Tooltip 代理，用于逃逸容器剪裁 -->
    <div
      v-show="tooltipProxy.show"
      class="mtga-tooltip-proxy"
      :style="{
        '--mtga-tooltip-max': tooltipProxy.maxWidth,
        ...tooltipProxy.style,
      }"
    >
      {{ tooltipProxy.content }}
    </div>
  </div>
</template>
