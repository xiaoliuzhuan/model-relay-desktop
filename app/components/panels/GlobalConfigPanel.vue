<script setup lang="ts">
import type { ConfigGroup, ProviderProtocol } from "~/composables/mtgaTypes";

const store = useMtgaStore();
const saving = ref(false);
const mappedModelId = computed({
  get: () => store.mappedModelId.value,
  set: (value) => {
    store.mappedModelId.value = value;
  },
});
const mtgaAuthKey = computed({
  get: () => store.mtgaAuthKey.value,
  set: (value) => {
    store.mtgaAuthKey.value = value;
  },
});

const officialModelNameCandidates = new Set([
  "claude-4.5-sonnet",
  "gemini-3-pro-preview",
  "gemini-3-flash-preview",
  "gemini-2.5-pro",
  "gemini-2.5-flash",
  "kimi-k2-0905",
  "kimi-k2.5",
  "gpt-5.3-codex",
  "gpt-5.2-codex",
  "gpt-5.2",
  "gpt-5.1",
  "gpt-5-medium",
  "gpt-5-high",
  "deepseek-v3.1",
  "glm-4.6",
]);

const relaySuffix = "-relay";

const normalizeModelId = (value: string) => value.trim().toLowerCase();

const ensureSafeMappedModelId = (value: string) => {
  const trimmed = value.trim();
  if (!trimmed) {
    return trimmed;
  }
  const normalized = normalizeModelId(trimmed);
  if (!officialModelNameCandidates.has(normalized)) {
    return trimmed;
  }
  if (normalized.endsWith(relaySuffix)) {
    return trimmed;
  }
  return `${trimmed}${relaySuffix}`;
};

const modelNameCollisionNotice = computed(() => {
  const currentModelId = mappedModelId.value.trim();
  if (!currentModelId) {
    return {
      show: false,
      matchedModelId: "",
    };
  }

  const normalizedModelId = normalizeModelId(currentModelId);
  if (!officialModelNameCandidates.has(normalizedModelId)) {
    return {
      show: false,
      matchedModelId: "",
    };
  }

  return {
    show: true,
    matchedModelId: currentModelId,
  };
});

const protocolLabelMap: Record<ProviderProtocol, string> = {
  openai: "OpenAI Chat Completions",
  anthropic_messages: "Anthropic Messages",
};

const normalizeProtocol = (value: string | undefined): ProviderProtocol =>
  value === "anthropic_messages" ? "anthropic_messages" : "openai";

const getGroupDisplayName = (group: ConfigGroup | undefined, index: number) =>
  group?.name?.trim() || `配置组 ${index + 1}`;

const protocolMixNotice = computed(() => {
  const groups = store.configGroups.value;
  if (!groups.length) {
    return {
      show: false,
      activeGroupName: "",
      activeProtocolLabel: "",
    };
  }

  const protocols = new Set<ProviderProtocol>();
  groups.forEach((group) => {
    protocols.add(normalizeProtocol(group.protocol));
  });

  if (!(protocols.has("openai") && protocols.has("anthropic_messages"))) {
    return {
      show: false,
      activeGroupName: "",
      activeProtocolLabel: "",
    };
  }

  const activeIndex = Math.min(Math.max(store.currentConfigIndex.value, 0), groups.length - 1);
  const activeGroup = groups[activeIndex];
  const activeProtocol = normalizeProtocol(activeGroup?.protocol);

  return {
    show: true,
    activeGroupName: getGroupDisplayName(activeGroup, activeIndex),
    activeProtocolLabel: protocolLabelMap[activeProtocol],
  };
});

const mappedModelTooltip = [
  "必填：客户端映射模型ID",
  "给 Trae/客户端填写的统一入口模型名。",
  "与各配置组中的“实际模型ID”互相独立。",
  "示例：assistant-router",
].join("\n");

const mtgaAuthTooltip = [
  "必填：客户端访问Key（本地代理）",
  "这是客户端访问本地代理入口的统一密钥。",
  "不等于 OpenAI/Anthropic 的上游 API Key。",
  "上游 API Key 请在各配置组中单独填写。",
  "示例：client-access-key",
].join("\n");

const handleSave = async () => {
  const currentMappedModelId = store.mappedModelId.value.trim();
  const safeMappedModelId = ensureSafeMappedModelId(currentMappedModelId);
  if (safeMappedModelId && safeMappedModelId !== currentMappedModelId) {
    store.mappedModelId.value = safeMappedModelId;
    store.appendLog(`检测到模型名与官方模型重合，已自动调整为: ${safeMappedModelId}`);
  }

  if (!store.mappedModelId.value || !store.mtgaAuthKey.value) {
    store.appendLog("错误: 客户端映射模型ID和客户端访问Key都是必填项");
    return;
  }
  saving.value = true;
  const ok = await store.saveConfig();
  saving.value = false;
  if (ok) {
    store.appendLog("全局配置已保存");
  } else {
    store.appendLog("保存全局配置失败");
  }
};
</script>

<template>
  <div class="flex items-center justify-between gap-3">
    <div>
      <h2 class="mtga-card-title">全局配置</h2>
      <p class="mtga-card-subtitle">管理客户端入口模型与本地代理鉴权</p>
    </div>
    <span class="mtga-chip">全局入口参数</span>
  </div>
  <div class="mt-4 space-y-4">
    <div class="alert alert-info rounded-xl py-2 px-3 text-xs">
      <span>
        说明：这里配置的是客户端访问本地代理的统一入口参数，不是上游厂商 API 参数。上游 API
        URL、模型ID、API Key 请在“代理配置组”中设置。
      </span>
    </div>

    <div v-if="protocolMixNotice.show" class="alert alert-warning rounded-xl py-2 px-3 text-xs">
      <span>
        检测到同时存在 OpenAI 与 Anthropic Messages 配置组。当前仅选中配置组生效：{{
          protocolMixNotice.activeGroupName
        }}（{{ protocolMixNotice.activeProtocolLabel }}）。
      </span>
    </div>

    <div class="mtga-soft-panel space-y-4">
      <div
        class="tooltip mtga-tooltip w-full"
        :data-tip="mappedModelTooltip"
        style="--mtga-tooltip-max: 360px"
      >
        <MtgaInput
          v-model="mappedModelId"
          label="客户端映射模型ID"
          placeholder="例如：assistant-router"
          required
        />
      </div>

      <div
        v-if="modelNameCollisionNotice.show"
        class="alert alert-warning rounded-xl py-2 px-3 text-xs"
      >
        <span>
          当前映射模型ID（{{ modelNameCollisionNotice.matchedModelId }}）与常见官方模型名重合，Trae
          可能误判为内置模型导致不走自定义通道。点击“保存全局配置”时会自动改为：{{
            modelNameCollisionNotice.matchedModelId
          }}-relay。
        </span>
      </div>

      <div
        class="tooltip mtga-tooltip w-full"
        :data-tip="mtgaAuthTooltip"
        style="--mtga-tooltip-max: 360px"
      >
        <MtgaInput
          v-model="mtgaAuthKey"
          label="客户端访问Key"
          placeholder="例如：client-access-key"
          type="password"
          required
        />
      </div>
    </div>

    <div class="flex items-center justify-between gap-3">
      <span class="text-xs text-slate-500">保存后会应用到所有配置组（仅入口参数）</span>
      <button class="btn btn-primary btn-sm px-4 rounded-xl" :disabled="saving" @click="handleSave">
        保存全局配置
      </button>
    </div>
  </div>
</template>
