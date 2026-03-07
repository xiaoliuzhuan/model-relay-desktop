<script setup lang="ts">
import type { MainTabKey } from "~/composables/mtgaTypes";

const tabs: { key: MainTabKey; label: string; description: string; badge: string }[] = [
  {
    key: "cert",
    label: "证书管理",
    description: "先生成并安装本地 CA / 服务器证书，建立系统信任基础。",
    badge: "步骤 1",
  },
  {
    key: "hosts",
    label: "hosts 文件",
    description: "确认导流域名映射、备份与恢复入口都在这一页完成。",
    badge: "步骤 2",
  },
  {
    key: "proxy",
    label: "代理服务",
    description: "最后调整运行选项，启动服务并检查网络环境是否就绪。",
    badge: "步骤 3",
  },
];

const activeTab = ref<MainTabKey>("cert");
const direction = ref<"right" | "left">("right");
const { mainTabTarget, mainTabSignal } = useMtgaStore();
const activeTabMeta = computed(() => tabs.find((tab) => tab.key === activeTab.value) ?? tabs[0]!);

/**
 * 处理标签页切换
 * @param key 目标标签页的键名
 */
const selectTab = (key: MainTabKey) => {
  const oldIndex = tabs.findIndex((t) => t.key === activeTab.value);
  const newIndex = tabs.findIndex((t) => t.key === key);

  if (newIndex !== oldIndex) {
    direction.value = newIndex > oldIndex ? "right" : "left";
    activeTab.value = key;
  }
};

const applyMainTabTarget = (target: MainTabKey | null) => {
  if (!target) {
    return;
  }
  selectTab(target);
};

watch(mainTabSignal, () => applyMainTabTarget(mainTabTarget.value), {
  immediate: true,
});
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div>
      <h2 class="mtga-card-title">主要流程</h2>
      <p class="mtga-card-subtitle">证书、hosts 与代理服务的标准操作流程</p>
    </div>
    <span class="mtga-chip">标准流程</span>
  </div>

  <div
    class="mt-5 rounded-2xl border border-indigo-100 bg-gradient-to-r from-white via-sky-50 to-indigo-50 px-4 py-3 text-sm text-slate-700 shadow-sm"
  >
    <p class="font-medium text-slate-900">建议顺序</p>
    <p class="mt-1 text-slate-600">先处理证书，再确认 hosts，最后启动代理服务并做网络检查。</p>
  </div>

  <div class="mt-4 rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
    <div class="flex items-center justify-between gap-3">
      <div>
        <p class="text-sm font-medium text-slate-900">流程导航</p>
        <p class="mt-1 text-xs text-slate-600">
          按步骤切换操作页，视觉上与全局配置保持同一套卡片语言
        </p>
      </div>
      <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs text-indigo-700">
        当前：{{ activeTabMeta.label }}
      </span>
    </div>

    <div role="tablist" class="mt-4 grid gap-3 lg:grid-cols-3">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        role="tab"
        type="button"
        class="rounded-2xl border p-4 text-left transition-all duration-150"
        :class="
          activeTab === tab.key
            ? 'border-indigo-300 bg-indigo-50/80 shadow-[0_10px_30px_-20px_rgba(79,70,229,0.45)]'
            : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-slate-50'
        "
        :aria-selected="activeTab === tab.key"
        @click="selectTab(tab.key)"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-base font-medium text-slate-900">{{ tab.label }}</p>
            <p class="mt-1 text-sm text-slate-600">{{ tab.description }}</p>
          </div>
          <span
            class="rounded-full px-2.5 py-1 text-[11px]"
            :class="
              activeTab === tab.key ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600'
            "
          >
            {{ activeTab === tab.key ? "当前步骤" : tab.badge }}
          </span>
        </div>
      </button>
    </div>
  </div>

  <div class="mt-4 rounded-2xl border border-slate-200/70 bg-white/45 p-2 shadow-sm">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      :enter-from-class="
        direction === 'right' ? 'opacity-0 translate-x-8' : 'opacity-0 -translate-x-8'
      "
      enter-to-class="opacity-100 translate-x-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-x-0"
      :leave-to-class="
        direction === 'right' ? 'opacity-0 -translate-x-8' : 'opacity-0 translate-x-8'
      "
      mode="out-in"
    >
      <div :key="activeTab" class="rounded-[20px] bg-slate-50/60 p-2">
        <section v-if="activeTab === 'cert'">
          <CertTab />
        </section>
        <section v-else-if="activeTab === 'hosts'">
          <HostsTab />
        </section>
        <section v-else-if="activeTab === 'proxy'">
          <ProxyTab />
        </section>
      </div>
    </Transition>
  </div>
</template>
