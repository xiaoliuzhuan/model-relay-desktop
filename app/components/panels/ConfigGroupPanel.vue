<script setup lang="ts">
import type { ConfigGroup } from "~/composables/mtgaTypes";

const store = useMtgaStore();
const configGroups = store.configGroups;
const currentIndex = store.currentConfigIndex;

const DEFAULT_MIDDLE_ROUTE = "/v1";

const editorOpen = ref(false);
const editorMode = ref<"add" | "edit">("add");
const formError = ref("");
const middleRouteEnabled = ref(false);
const availableModels = ref<string[]>([]);
const modelLoading = ref(false);

const confirmOpen = ref(false);
const confirmTitle = ref("确认删除");
const confirmMessage = ref("");
const pendingDeleteIndex = ref<number | null>(null);
const pendingSwitchIndex = ref<number | null>(null);
const switchInProgress = ref(false);

const form = reactive({
  name: "",
  api_url: "",
  model_id: "",
  api_key: "",
  protocol: "openai" as "openai" | "anthropic_messages",
  middle_route: "",
});

const testTooltip = [
  "测试选中配置组的实际对话功能",
  "会发送最小请求并消耗少量tokens",
  "请确保配置正确后使用",
].join("\n");

const refreshTooltip = ["重新加载配置文件中的配置组", "用于同步外部修改或恢复意外更改"].join("\n");

const selectedIndex = computed({
  get: () => (configGroups.value.length ? currentIndex.value : -1),
  set: (value) => {
    if (value < 0 || value >= configGroups.value.length) {
      return;
    }
    if (value === currentIndex.value && pendingSwitchIndex.value === null) {
      return;
    }
    currentIndex.value = value;
    pendingSwitchIndex.value = value;
    void processConfigSwitch();
  },
});

const processConfigSwitch = async () => {
  if (switchInProgress.value) {
    return;
  }
  switchInProgress.value = true;
  try {
    while (pendingSwitchIndex.value !== null) {
      const targetIndex = pendingSwitchIndex.value;
      pendingSwitchIndex.value = null;
      currentIndex.value = targetIndex;

      const saved = await store.saveConfig();
      if (!saved) {
        store.appendLog("保存配置组失败");
        continue;
      }

      // 若有新的切换请求，跳过当前热应用，直接处理最新选择。
      if (pendingSwitchIndex.value !== null) {
        continue;
      }
      await store.runProxyApplyCurrentConfig();
    }
  } finally {
    switchInProgress.value = false;
  }
};

const hasSelection = computed(
  () =>
    configGroups.value.length > 0 &&
    selectedIndex.value >= 0 &&
    selectedIndex.value < configGroups.value.length,
);

const selectedGroup = computed(() =>
  hasSelection.value ? configGroups.value[selectedIndex.value] || null : null,
);

const getProtocolLabel = (group: Pick<ConfigGroup, "protocol"> | null | undefined) => {
  if (!group) {
    return "未配置";
  }
  return group.protocol === "anthropic_messages" ? "Anthropic Messages" : "OpenAI";
};

const selectedGroupSummary = computed(() => {
  if (!hasSelection.value) {
    return {
      name: "未选择",
      protocol: "未配置",
      apiUrl: "未配置",
      modelId: "未配置",
    };
  }

  return {
    name: selectedGroup.value ? getDisplayName(selectedGroup.value, selectedIndex.value) : "未选择",
    protocol: getProtocolLabel(selectedGroup.value),
    apiUrl: selectedGroup.value?.api_url || "未配置",
    modelId: selectedGroup.value?.model_id || "未配置",
  };
});

const configStats = computed(() => {
  const groups = configGroups.value;
  return {
    total: groups.length,
    openai: groups.filter((group) => group.protocol !== "anthropic_messages").length,
    anthropic: groups.filter((group) => group.protocol === "anthropic_messages").length,
  };
});

const normalizeMiddleRoute = (value: string) => {
  let raw = value.trim();
  if (!raw) {
    raw = DEFAULT_MIDDLE_ROUTE;
  }
  if (!raw.startsWith("/")) {
    raw = `/${raw}`;
  }
  if (raw.length > 1) {
    raw = raw.replace(/\/+$/, "");
    if (!raw) {
      raw = "/";
    }
  }
  return raw;
};

const getDisplayName = (group: ConfigGroup, index: number) =>
  group.name?.trim() || `配置组 ${index + 1}`;

/**
 * 获取 API Key 的显示文本
 * 规则：
 * 1. 长度 <= 12 位时，全部显示为星号
 * 2. 长度 > 12 位时，每超出一位显示一位明文，上限为 4 位明文
 * 3. 显示的总长度（星号+明文）与实际长度一致
 */
const getApiKeyDisplay = (group: ConfigGroup) => {
  if ("target_model_id" in group) {
    return group.target_model_id || "(无)";
  }
  const apiKey = group.api_key || "";
  if (!apiKey) {
    return "(无)";
  }

  const len = apiKey.length;
  const threshold = 12;
  const maxVisible = 4;

  // 计算可见字符数：超出阈值的部分，且不超过上限
  const visibleCount = Math.min(Math.max(0, len - threshold), maxVisible);

  if (visibleCount > 0) {
    return `${"*".repeat(len - visibleCount)}${apiKey.slice(-visibleCount)}`;
  }
  return "*".repeat(len);
};

const refreshList = async () => {
  const ok = await store.loadConfig();
  if (ok) {
    store.appendLog("已刷新配置组列表");
  }
};

const requestTest = async () => {
  if (!hasSelection.value) {
    store.appendLog("请先选择要测活的配置组");
    return;
  }
  await store.runConfigGroupTest(selectedIndex.value);
};

const resetForm = () => {
  form.name = "";
  form.api_url = "";
  form.model_id = "";
  form.api_key = "";
  form.protocol = "openai";
  form.middle_route = "";
  middleRouteEnabled.value = false;
  formError.value = "";
  availableModels.value = [];
  modelLoading.value = false;
};

const openAdd = () => {
  editorMode.value = "add";
  resetForm();
  editorOpen.value = true;
};

const openEdit = () => {
  if (!hasSelection.value) {
    store.appendLog("请先选择要修改的配置组");
    return;
  }
  editorMode.value = "edit";
  const group = configGroups.value[selectedIndex.value];
  if (!group) {
    return;
  }
  form.name = group.name || "";
  form.api_url = group.api_url || "";
  form.model_id = group.model_id || "";
  form.api_key = group.api_key || "";
  form.protocol = group.protocol || "openai";
  form.middle_route = group.middle_route || "";
  middleRouteEnabled.value = Boolean(group.middle_route);
  formError.value = "";
  availableModels.value = [];
  editorOpen.value = true;
};

const closeEditor = () => {
  editorOpen.value = false;
};

const handleSave = async () => {
  const payload: ConfigGroup = {
    name: form.name.trim(),
    api_url: form.api_url.trim(),
    model_id: form.model_id.trim(),
    api_key: form.api_key.trim(),
    protocol: form.protocol,
  };

  if (!payload.api_url || !payload.model_id || !payload.api_key) {
    formError.value = "API URL、实际模型ID 和 API Key 都是必填项";
    store.appendLog("错误: API URL、实际模型ID和API Key都是必填项");
    return;
  }

  if (middleRouteEnabled.value && form.middle_route.trim()) {
    payload.middle_route = normalizeMiddleRoute(form.middle_route);
  }

  if (editorMode.value === "add") {
    configGroups.value.push(payload);
    currentIndex.value = configGroups.value.length - 1;
  } else if (hasSelection.value) {
    configGroups.value.splice(selectedIndex.value, 1, payload);
  }

  const ok = await store.saveConfig();
  if (ok) {
    const displayName = getDisplayName(payload, selectedIndex.value);
    store.appendLog(
      editorMode.value === "add" ? `已添加配置组: ${displayName}` : `已修改配置组: ${displayName}`,
    );
    closeEditor();
  } else {
    store.appendLog("保存配置组失败");
  }
};

const handleFetchModels = async () => {
  if (modelLoading.value) {
    return;
  }
  const apiUrl = form.api_url.trim();
  if (!apiUrl) {
    store.appendLog("获取模型列表失败: API URL为空");
    return;
  }
  modelLoading.value = true;
  const models = await store.fetchConfigGroupModels({
    api_url: apiUrl,
    api_key: form.api_key.trim(),
    model_id: form.model_id.trim(),
    protocol: form.protocol,
    middle_route: middleRouteEnabled.value ? normalizeMiddleRoute(form.middle_route) : "",
  });
  if (models !== null) {
    availableModels.value = models;
  }
  modelLoading.value = false;
};

const requestDelete = () => {
  if (!hasSelection.value) {
    store.appendLog("请先选择要删除的配置组");
    return;
  }
  if (configGroups.value.length <= 1) {
    store.appendLog("至少需要保留一个配置组");
    return;
  }
  const group = configGroups.value[selectedIndex.value];
  if (!group) {
    return;
  }
  pendingDeleteIndex.value = selectedIndex.value;
  confirmTitle.value = "确认删除";
  confirmMessage.value = `确定要删除配置组 “${getDisplayName(group, selectedIndex.value)}” 吗？`;
  confirmOpen.value = true;
};

const cancelDelete = () => {
  confirmOpen.value = false;
  pendingDeleteIndex.value = null;
};

const confirmDelete = async () => {
  if (pendingDeleteIndex.value == null) {
    return;
  }
  const index = pendingDeleteIndex.value;
  const group = configGroups.value[index];
  if (!group) {
    store.appendLog("配置组不存在，已取消删除");
    confirmOpen.value = false;
    pendingDeleteIndex.value = null;
    return;
  }
  configGroups.value.splice(index, 1);
  if (currentIndex.value >= configGroups.value.length) {
    currentIndex.value = Math.max(configGroups.value.length - 1, 0);
  } else if (currentIndex.value > index) {
    currentIndex.value -= 1;
  }
  const ok = await store.saveConfig();
  if (ok) {
    store.appendLog(`已删除配置组: ${getDisplayName(group, index)}`);
  } else {
    store.appendLog("保存配置组失败");
  }
  confirmOpen.value = false;
  pendingDeleteIndex.value = null;
};

const moveUp = async () => {
  if (!hasSelection.value || selectedIndex.value <= 0) {
    return;
  }
  const index = selectedIndex.value;
  const current = configGroups.value[index];
  const prev = configGroups.value[index - 1];
  if (!current || !prev) {
    return;
  }
  configGroups.value[index - 1] = current;
  configGroups.value[index] = prev;
  currentIndex.value = index - 1;
  await store.saveConfig();
};

const moveDown = async () => {
  if (!hasSelection.value || selectedIndex.value >= configGroups.value.length - 1) {
    return;
  }
  const index = selectedIndex.value;
  const current = configGroups.value[index];
  const next = configGroups.value[index + 1];
  if (!current || !next) {
    return;
  }
  configGroups.value[index + 1] = current;
  configGroups.value[index] = next;
  currentIndex.value = index + 1;
  await store.saveConfig();
};
</script>

<template>
  <div class="flex flex-wrap items-start justify-between gap-3">
    <div>
      <h2 class="mtga-card-title">代理服务器配置组</h2>
      <p class="mtga-card-subtitle">管理上游协议、模型路由与鉴权组合</p>
    </div>
    <span class="mtga-chip">配置组管理</span>
  </div>

  <div class="mt-5 mtga-panel-banner">
    <p class="font-medium text-slate-900">配置组决定真正生效的上游协议</p>
    <p class="mt-1 text-slate-600">
      Trae / Cursor 入口参数在全局页维护；真正走 OpenAI 还是 Anthropic，由这里当前选中的配置组决定。
    </p>
  </div>

  <div class="mt-4 mtga-panel-card">
    <div class="grid gap-3 sm:grid-cols-4">
      <div class="rounded-xl bg-slate-50 px-4 py-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">配置组总数</p>
        <p class="mt-1 text-sm text-slate-900">{{ configStats.total }}</p>
      </div>
      <div class="rounded-xl bg-slate-50 px-4 py-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">OpenAI 组</p>
        <p class="mt-1 text-sm text-slate-900">{{ configStats.openai }}</p>
      </div>
      <div class="rounded-xl bg-slate-50 px-4 py-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">Anthropic 组</p>
        <p class="mt-1 text-sm text-slate-900">{{ configStats.anthropic }}</p>
      </div>
      <div class="rounded-xl bg-slate-50 px-4 py-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">当前选中</p>
        <p class="mt-1 break-all text-sm text-slate-900">{{ selectedGroupSummary.name }}</p>
      </div>
    </div>

    <div class="mt-3 grid gap-3 sm:grid-cols-3">
      <div class="rounded-xl border border-slate-200/80 bg-white px-4 py-3">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">当前协议</p>
        <p class="mt-1 text-sm text-slate-900">{{ selectedGroupSummary.protocol }}</p>
      </div>
      <div class="rounded-xl border border-slate-200/80 bg-white px-4 py-3 sm:col-span-2">
        <p class="text-[11px] uppercase tracking-wide text-slate-400">当前 API URL / 模型</p>
        <p class="mt-1 break-all text-sm text-slate-900">
          {{ selectedGroupSummary.apiUrl }} · {{ selectedGroupSummary.modelId }}
        </p>
      </div>
    </div>
  </div>

  <div class="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.95fr)]">
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
          @click="refreshList"
        >
          刷新列表
        </button>
      </div>

      <div v-if="configGroups.length" class="mt-4 grid gap-3 lg:grid-cols-2">
        <button
          v-for="(group, index) in configGroups"
          :key="index"
          type="button"
          class="rounded-2xl border p-4 text-left transition-all duration-150"
          :class="
            selectedIndex === index
              ? 'border-indigo-300 bg-indigo-50/80 shadow-[0_10px_30px_-20px_rgba(79,70,229,0.45)]'
              : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-slate-50'
          "
          :title="group.name || ''"
          @click="selectedIndex = index"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="break-all text-base font-medium text-slate-900">
                  {{ getDisplayName(group, index) }}
                </p>
                <span
                  class="shrink-0 rounded-full px-2.5 py-1 text-[11px]"
                  :class="
                    selectedIndex === index
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 text-slate-600'
                  "
                >
                  {{ selectedIndex === index ? "当前生效" : `#${index + 1}` }}
                </span>
              </div>
              <p class="mt-1 break-all text-sm text-slate-600">
                {{ getProtocolLabel(group) }}
                <span v-if="group.middle_route"> · {{ group.middle_route }}</span>
              </p>
            </div>
            <span
              class="shrink-0 rounded-full px-2.5 py-1 text-[11px]"
              :class="
                group.protocol === 'anthropic_messages'
                  ? 'bg-amber-100 text-amber-700'
                  : 'bg-emerald-100 text-emerald-700'
              "
            >
              {{ group.protocol === "anthropic_messages" ? "Anthropic" : "OpenAI" }}
            </span>
          </div>

          <div class="mt-4 rounded-xl border border-slate-200/80 bg-white/80 p-3">
            <p class="text-[11px] uppercase tracking-wide text-slate-400">上游参数</p>
            <div class="mt-3 space-y-2">
              <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
                <span class="text-xs text-slate-500">API URL</span>
                <span class="break-all text-right text-sm text-slate-800">
                  {{ group.api_url || "未填写" }}
                </span>
              </div>
              <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
                <span class="text-xs text-slate-500">模型 ID</span>
                <span class="break-all text-right text-sm text-slate-800">
                  {{ group.model_id || "未填写" }}
                </span>
              </div>
              <div class="flex items-start justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
                <span class="text-xs text-slate-500">API Key</span>
                <span class="break-all text-right text-sm text-slate-800">
                  {{ getApiKeyDisplay(group) }}
                </span>
              </div>
            </div>
          </div>

          <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
            <span class="text-xs text-slate-500">切换后会保存并热应用当前配置组</span>
            <span
              class="inline-flex items-center rounded-full px-2 py-1 text-[11px]"
              :class="
                selectedIndex === index
                  ? 'bg-emerald-100 text-emerald-700'
                  : 'bg-slate-100 text-slate-500'
              "
            >
              {{ selectedIndex === index ? "已选中" : "点击设为当前" }}
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

    <div class="space-y-4">
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
          <div class="flex items-start justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3">
            <span class="text-xs text-slate-500">配置组</span>
            <span class="break-all text-right text-sm text-slate-900">
              {{ selectedGroupSummary.name }}
            </span>
          </div>
          <div class="flex items-start justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3">
            <span class="text-xs text-slate-500">上游协议</span>
            <span class="break-all text-right text-sm text-slate-900">
              {{ selectedGroupSummary.protocol }}
            </span>
          </div>
          <div class="flex items-start justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3">
            <span class="text-xs text-slate-500">API URL</span>
            <span class="break-all text-right text-sm text-slate-900">
              {{ selectedGroupSummary.apiUrl }}
            </span>
          </div>
          <div class="flex items-start justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3">
            <span class="text-xs text-slate-500">模型 ID</span>
            <span class="break-all text-right text-sm text-slate-900">
              {{ selectedGroupSummary.modelId }}
            </span>
          </div>
          <div class="flex items-start justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3">
            <span class="text-xs text-slate-500">API Key</span>
            <span class="break-all text-right text-sm text-slate-900">
              {{ selectedGroup ? getApiKeyDisplay(selectedGroup) : "未配置" }}
            </span>
          </div>
          <div class="flex items-start justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3">
            <span class="text-xs text-slate-500">中转路径</span>
            <span class="break-all text-right text-sm text-slate-900">
              {{ selectedGroup?.middle_route || `默认 ${DEFAULT_MIDDLE_ROUTE}` }}
            </span>
          </div>
        </div>

        <div
          class="mt-4 rounded-xl border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-slate-700"
        >
          切换配置组时会先保存当前索引，再热应用选中的协议与路由，减少多协议共存时的误读。
        </div>
      </div>

      <div class="mtga-panel-card">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-sm font-medium text-slate-900">快捷操作</p>
            <p class="mt-1 text-xs text-slate-600">新增、维护顺序或对当前组做编辑与测活</p>
          </div>
          <button
            class="btn btn-xs btn-outline shrink-0 rounded-lg border-slate-200 px-3 text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700 tooltip mtga-tooltip"
            :data-tip="testTooltip"
            style="--mtga-tooltip-max: 250px"
            @click="requestTest"
          >
            测活
          </button>
        </div>

        <div class="mt-4 grid gap-2 sm:grid-cols-2">
          <button class="mtga-btn-primary" @click="openAdd">新增配置组</button>
          <button class="mtga-btn-outline" @click="openEdit">修改当前组</button>
          <button class="mtga-btn-error" @click="requestDelete">删除当前组</button>
          <button class="mtga-btn-outline" @click="moveUp">上移当前组</button>
          <button class="mtga-btn-outline sm:col-span-2" @click="moveDown">下移当前组</button>
        </div>

        <p class="mt-3 text-xs text-slate-500">
          删除、修改、排序都会基于当前选中的配置组执行；删除时仍会至少保留一个配置组。
        </p>
      </div>
    </div>
  </div>

  <ConfigGroupEditorDialog
    v-model:open="editorOpen"
    v-model:name="form.name"
    v-model:api-url="form.api_url"
    v-model:model-id="form.model_id"
    v-model:api-key="form.api_key"
    v-model:protocol="form.protocol"
    v-model:middle-route="form.middle_route"
    v-model:middle-route-enabled="middleRouteEnabled"
    :mode="editorMode"
    :form-error="formError"
    :default-middle-route="DEFAULT_MIDDLE_ROUTE"
    :available-models="availableModels"
    :model-loading="modelLoading"
    @fetch-models="handleFetchModels"
    @save="handleSave"
    @cancel="closeEditor"
  />

  <ConfirmDialog
    :open="confirmOpen"
    :title="confirmTitle"
    :message="confirmMessage"
    type="error"
    @cancel="cancelDelete"
    @confirm="confirmDelete"
  />
</template>
