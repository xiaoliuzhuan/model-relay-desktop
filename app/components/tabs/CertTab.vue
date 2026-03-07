<script setup lang="ts">
const store = useMtgaStore();
const appInfo = store.appInfo;
const caCommonName = computed(() => appInfo.value.ca_common_name || "MODEL_RELAY_DESKTOP_CA");

const isConfirmOpen = ref(false);
const inputCommonName = ref("");
const showInputError = ref(false);

const clearCaTooltip = computed(() => {
  return [
    "macOS: 删除系统钥匙串中匹配的CA证书；",
    "Windows: 删除本地计算机/Root 中匹配的CA证书",
    `Common Name: ${caCommonName.value}`,
    "需要管理员权限，建议仅在需要重置证书时使用",
  ].join("\n");
});

const handleGenerate = () => {
  store.runGenerateCertificates();
};

const handleInstall = () => {
  store.runInstallCaCert();
};

/**
 * 触发清除系统 CA 证书流程，先打开确认弹窗
 */
const handleClear = () => {
  inputCommonName.value = caCommonName.value;
  showInputError.value = false;
  isConfirmOpen.value = true;
};

/**
 * 用户确认后的实际清除操作
 */
const confirmClear = () => {
  if (!inputCommonName.value.trim()) {
    showInputError.value = true;
    return;
  }
  isConfirmOpen.value = false;
  store.runClearCaCert(inputCommonName.value);
};

watch(inputCommonName, (val) => {
  if (val.trim()) {
    showInputError.value = false;
  }
});
</script>

<template>
  <div class="space-y-4">
    <div class="mtga-panel-card">
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="text-sm font-medium text-slate-900">证书管理</div>
          <div class="mt-1 text-xs text-slate-600">
            为本地代理建立 CA 信任链，并在需要时做安全清理
          </div>
        </div>
        <span class="mtga-status-pill"> Common Name：{{ caCommonName }} </span>
      </div>

      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div class="mtga-panel-tile">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">推荐流程</p>
          <p class="mt-1 text-sm text-slate-900">先生成证书，再安装 CA 到系统信任存储</p>
        </div>
        <div class="mtga-panel-tile">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">适用场景</p>
          <p class="mt-1 text-sm text-slate-900">首次配置、证书重置或切换到新环境时使用</p>
        </div>
      </div>
    </div>

    <div class="grid gap-4 lg:grid-cols-[minmax(0,1.15fr)_minmax(280px,0.85fr)]">
      <div class="mtga-panel-card">
        <div>
          <div class="text-sm font-medium text-slate-900">生成与安装</div>
          <div class="mt-1 text-xs text-slate-600">主流程集中在这里，适合按顺序完成初始化</div>
        </div>
        <div class="mt-4 grid gap-2 sm:grid-cols-2">
          <button class="mtga-btn-primary" @click="handleGenerate">生成 CA 与服务器证书</button>
          <button class="mtga-btn-outline" @click="handleInstall">安装 CA 证书</button>
        </div>
        <p class="mt-3 text-xs text-slate-500">
          若已经生成过证书，可直接重新安装 CA；首次配置建议按按钮从左到右执行。
        </p>
      </div>

      <div class="rounded-2xl border border-amber-200 bg-amber-50/80 p-4 shadow-sm">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="text-sm font-medium text-amber-900">清理系统 CA</div>
            <div class="mt-1 text-xs text-amber-700">仅在需要重置、卸载或排查信任链异常时使用</div>
          </div>
          <span
            class="inline-flex shrink-0 items-center rounded-full bg-white/80 px-3 py-1 text-xs text-amber-700 shadow-sm"
            >谨慎操作</span
          >
        </div>
        <p class="mt-4 text-sm text-amber-900">
          将按 Common Name 匹配并删除系统信任存储中的 CA 证书。
        </p>
        <button
          class="mtga-btn-error mt-4 tooltip mtga-tooltip"
          :data-tip="clearCaTooltip"
          style="--mtga-tooltip-max: 280px"
          @click="handleClear"
        >
          清除系统 CA 证书
        </button>
      </div>
    </div>
  </div>

  <!-- 二次确认弹窗 -->
  <ConfirmDialog
    v-model:open="isConfirmOpen"
    v-model="inputCommonName"
    title="确认清除 CA 证书"
    message="将从系统信任存储中删除匹配的 CA 证书，是否继续？"
    show-input
    label="Common Name:"
    placeholder="请输入证书 Common Name"
    :error="showInputError ? '请输入有效的 Common Name' : ''"
    input-class="font-mono"
    confirm-text="确认清除"
    type="error"
    @confirm="confirmClear"
  />
</template>
