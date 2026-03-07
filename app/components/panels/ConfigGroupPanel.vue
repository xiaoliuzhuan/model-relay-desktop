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
  const visibleCount = Math.min(Math.max(0, len - threshold), maxVisible);

  if (visibleCount > 0) {
    return `${"*".repeat(len - visibleCount)}${apiKey.slice(-visibleCount)}`;
  }
  return "*".repeat(len);
};

const configGroupItems = computed(() =>
  configGroups.value.map((group, index) => {
    const isSelected = selectedIndex.value === index;
    const isAnthropic = group.protocol === "anthropic_messages";

    return {
      index,
      title: group.name || "",
      displayName: getDisplayName(group, index),
      selectionBadgeLabel: isSelected ? "当前生效" : `#${index + 1}`,
      selectionBadgeClass: isSelected ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600",
      protocolText: getProtocolLabel(group),
      protocolBadgeLabel: isAnthropic ? "Anthropic" : "OpenAI",
      protocolBadgeClass: isAnthropic
        ? "bg-amber-100 text-amber-700"
        : "bg-emerald-100 text-emerald-700",
      middleRoute: group.middle_route || "",
      apiUrl: group.api_url || "未填写",
      modelId: group.model_id || "未填写",
      apiKeyDisplay: getApiKeyDisplay(group),
      selectionHintLabel: isSelected ? "已选中" : "点击设为当前",
      selectionHintClass: isSelected
        ? "bg-emerald-100 text-emerald-700"
        : "bg-slate-100 text-slate-500",
    };
  }),
);

const selectedApiKeyDisplay = computed(() =>
  selectedGroup.value ? getApiKeyDisplay(selectedGroup.value) : "未配置",
);

const selectedMiddleRouteLabel = computed(
  () => selectedGroup.value?.middle_route || `默认 ${DEFAULT_MIDDLE_ROUTE}`,
);

const selectConfigGroup = (value: number) => {
  selectedIndex.value = value;
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

  <ConfigGroupOverviewSection :stats="configStats" :summary="selectedGroupSummary" />

  <div class="mt-4 grid gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.95fr)]">
    <ConfigGroupListSection
      :items="configGroupItems"
      :refresh-tooltip="refreshTooltip"
      @refresh="refreshList"
      @select="selectConfigGroup"
    />

    <div class="space-y-4">
      <ConfigGroupSelectedDetailSection
        :has-selection="hasSelection"
        :summary="selectedGroupSummary"
        :api-key-display="selectedApiKeyDisplay"
        :middle-route-label="selectedMiddleRouteLabel"
      />

      <ConfigGroupActionsSection
        :test-tooltip="testTooltip"
        @test="requestTest"
        @add="openAdd"
        @edit="openEdit"
        @delete="requestDelete"
        @move-up="moveUp"
        @move-down="moveDown"
      />
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
