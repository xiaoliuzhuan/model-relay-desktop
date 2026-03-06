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
const cursorNamespacePrefix = "mr-cursor-";
const clientProfileStorageKey = "mtga-client-profile";

type ClientProfile = "trae" | "cursor" | "generic";

const clientProfile = ref<ClientProfile>("trae");

const clientProfileLabelMap: Record<ClientProfile, string> = {
  trae: "Trae",
  cursor: "Cursor",
  generic: "通用客户端",
};

const protocolLabelMap: Record<ProviderProtocol, string> = {
  openai: "OpenAI Chat Completions",
  anthropic_messages: "Anthropic Messages",
};

const normalizeModelId = (value: string) => value.trim().toLowerCase();

const normalizeProtocol = (value: string | undefined): ProviderProtocol =>
  value === "anthropic_messages" ? "anthropic_messages" : "openai";

const getGroupDisplayName = (group: ConfigGroup | undefined, index: number) =>
  group?.name?.trim() || `配置组 ${index + 1}`;

const ensureSafeMappedModelId = (value: string, profile: ClientProfile) => {
  const trimmed = value.trim();
  if (!trimmed) {
    return trimmed;
  }

  const normalized = normalizeModelId(trimmed);
  if (profile === "cursor") {
    if (normalized.startsWith(cursorNamespacePrefix)) {
      return trimmed;
    }
    return `${cursorNamespacePrefix}${trimmed}`;
  }

  if (!officialModelNameCandidates.has(normalized)) {
    return trimmed;
  }
  if (normalized.endsWith(relaySuffix)) {
    return trimmed;
  }
  return `${trimmed}${relaySuffix}`;
};

const currentMappedModelId = computed(() => mappedModelId.value.trim());

const buildPreviewMappedModelId = (profile: ClientProfile) => {
  const fallbackByProfile: Record<ClientProfile, string> = {
    trae: "assistant-router",
    cursor: "claude-4.5-sonnet",
    generic: "assistant-router",
  };
  const sourceModelId = currentMappedModelId.value || fallbackByProfile[profile];
  return ensureSafeMappedModelId(sourceModelId, profile);
};

const modelNameCollisionNotice = computed(() => {
  const currentModel = currentMappedModelId.value;
  if (!currentModel) {
    return {
      show: false,
      matchedModelId: "",
      suggestion: "",
    };
  }

  const normalizedModelId = normalizeModelId(currentModel);
  const collidesWithOfficial = officialModelNameCandidates.has(normalizedModelId);
  if (!collidesWithOfficial && clientProfile.value !== "cursor") {
    return {
      show: false,
      matchedModelId: "",
      suggestion: "",
    };
  }

  const suggestion = ensureSafeMappedModelId(currentModel, clientProfile.value);
  if (suggestion === currentModel && !collidesWithOfficial) {
    return {
      show: false,
      matchedModelId: "",
      suggestion: "",
    };
  }

  return {
    show: true,
    matchedModelId: currentModel,
    suggestion,
  };
});

const activeGroupSummary = computed(() => {
  const groups = store.configGroups.value;
  if (!groups.length) {
    return {
      groupName: "未配置",
      protocolLabel: "未配置",
      targetModelId: "未配置",
    };
  }

  const activeIndex = Math.min(Math.max(store.currentConfigIndex.value, 0), groups.length - 1);
  const activeGroup = groups[activeIndex];
  const activeProtocol = normalizeProtocol(activeGroup?.protocol);

  return {
    groupName: getGroupDisplayName(activeGroup, activeIndex),
    protocolLabel: protocolLabelMap[activeProtocol],
    targetModelId: activeGroup?.model_id?.trim() || "未配置",
  };
});

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

  return {
    show: true,
    activeGroupName: activeGroupSummary.value.groupName,
    activeProtocolLabel: activeGroupSummary.value.protocolLabel,
  };
});

const clientGuides = computed(() => [
  {
    id: "trae" as const,
    title: "Trae",
    badge: "推荐",
    description: "适合在 Trae 中直接添加 OpenAI / Anthropic 模型入口。",
    modelPreview: buildPreviewMappedModelId("trae"),
    namingHint: "若命中官方模型名，将自动追加 -relay，避免与内置模型重名。",
  },
  {
    id: "cursor" as const,
    title: "Cursor",
    badge: "重点标记",
    description: "适合在 Cursor 中配置自定义模型，优先使用命名空间策略。",
    modelPreview: buildPreviewMappedModelId("cursor"),
    namingHint: "保存时会自动改成 mr-cursor-*，最大程度规避与官方内置模型冲突。",
  },
]);

const selectedClientGuide = computed(() => {
  const guide = clientGuides.value.find((item) => item.id === clientProfile.value);
  return (
    guide || {
      id: "generic" as const,
      title: clientProfileLabelMap.generic,
      badge: "通用",
      description: "适用于通用 OpenAI 兼容客户端。",
      modelPreview: buildPreviewMappedModelId("generic"),
      namingHint: "建议使用不与官方模型重名的入口模型名。",
    }
  );
});

const copiedGuideId = ref<ClientProfile | null>(null);
const copyToastMessage = ref("");

const showCopyToast = (message: string) => {
  copyToastMessage.value = message;
  window.setTimeout(() => {
    if (copyToastMessage.value === message) {
      copyToastMessage.value = "";
    }
  }, 1800);
};

const mappedModelDescription = computed(() => {
  return `当前按 ${selectedClientGuide.value.title} 场景建议使用：${selectedClientGuide.value.modelPreview}`;
});

const mtgaAuthDescription =
  "客户端访问本地代理入口时使用的统一密钥，不等于上游 OpenAI / Anthropic API Key。";

const buildClientGuideCopyText = (profile: ClientProfile) => {
  const previewModelId = buildPreviewMappedModelId(profile);
  const keyPreview = mtgaAuthKey.value.trim() || "<客户端访问Key>";

  if (profile === "cursor") {
    return [
      "【Cursor 配置】",
      "- 客户端类型：Cursor",
      "- Base URL：本地代理地址（OpenAI 兼容入口）",
      `- Model：${previewModelId}`,
      `- API Key：${keyPreview}`,
      "- 说明：建议保持当前配置组与目标上游协议一致后再使用。",
    ].join("\n");
  }

  if (profile === "trae") {
    return [
      "【Trae 配置】",
      "- OpenAI 服务商：Model 填入口模型名，API Key 填客户端访问Key",
      "- Anthropic 服务商：Model 填入口模型名，API Key 填客户端访问Key",
      `- Model：${previewModelId}`,
      `- API Key：${keyPreview}`,
      "- 说明：Trae 中可同时存在 OpenAI / Anthropic 两条配置。",
    ].join("\n");
  }

  return [
    "【通用客户端配置】",
    "- 使用 OpenAI 兼容模式接入本地代理",
    `- Model：${previewModelId}`,
    `- API Key：${keyPreview}`,
  ].join("\n");
};

const copyClientGuide = async (profile: ClientProfile) => {
  try {
    await navigator.clipboard.writeText(buildClientGuideCopyText(profile));
    copiedGuideId.value = profile;
    store.appendLog(`已复制 ${clientProfileLabelMap[profile]} 配置说明`);
    showCopyToast(`已复制 ${clientProfileLabelMap[profile]} 配置说明`);
    window.setTimeout(() => {
      if (copiedGuideId.value === profile) {
        copiedGuideId.value = null;
      }
    }, 1800);
  } catch {
    store.appendLog(`复制 ${clientProfileLabelMap[profile]} 配置说明失败`);
  }
};

const copyFieldValue = async (kind: "model" | "key") => {
  const value = kind === "model" ? mappedModelId.value.trim() : mtgaAuthKey.value.trim();
  if (!value) {
    store.appendLog(kind === "model" ? "暂无可复制的模型名" : "暂无可复制的访问Key");
    return;
  }

  try {
    await navigator.clipboard.writeText(value);
    const successMessage = kind === "model" ? "已复制客户端映射模型ID" : "已复制客户端访问Key";
    store.appendLog(successMessage);
    showCopyToast(successMessage);
  } catch {
    store.appendLog(kind === "model" ? "复制客户端映射模型ID失败" : "复制客户端访问Key失败");
  }
};

const jumpToConfigGroup = () => {
  store.panelNavTarget.value = "config-group";
  store.panelNavSignal.value += 1;
};

const selectClientProfile = (profile: ClientProfile) => {
  clientProfile.value = profile;
};

onMounted(() => {
  const storedProfile = localStorage.getItem(clientProfileStorageKey);
  if (storedProfile === "trae" || storedProfile === "cursor" || storedProfile === "generic") {
    clientProfile.value = storedProfile;
  }
});

watch(clientProfile, (profile) => {
  localStorage.setItem(clientProfileStorageKey, profile);
});

const handleSave = async () => {
  const safeMappedModelId = ensureSafeMappedModelId(
    currentMappedModelId.value,
    clientProfile.value,
  );
  if (safeMappedModelId && safeMappedModelId !== currentMappedModelId.value) {
    store.mappedModelId.value = safeMappedModelId;
    store.appendLog(
      `已按 ${selectedClientGuide.value.title} 规则自动调整模型入口名: ${safeMappedModelId}`,
    );
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
  <div class="flex items-start justify-between gap-4">
    <div>
      <h2 class="mtga-card-title">全局入口配置</h2>
      <p class="mtga-card-subtitle">统一客户端入口，协议与上游参数仍由配置组控制</p>
    </div>
    <span class="mtga-chip shrink-0">客户端入口参数</span>
  </div>

  <div class="mt-5 space-y-4">
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="translate-y-1 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-1 opacity-0"
    >
      <div
        v-if="copyToastMessage"
        class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700 shadow-sm"
      >
        {{ copyToastMessage }}
      </div>
    </Transition>
    <div
      class="rounded-2xl border border-indigo-100 bg-gradient-to-r from-white via-sky-50 to-indigo-50 px-4 py-3 text-sm text-slate-700 shadow-sm"
    >
      <p class="font-medium text-slate-900">这一页只做两件事</p>
      <p class="mt-1 text-slate-600">
        维护客户端统一入口模型名与访问密钥，不承载上游 API URL、上游模型ID、上游 API Key。
      </p>
    </div>

    <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-medium text-slate-900">Trae / Cursor 双端接入</p>
          <p class="mt-1 text-xs text-slate-600">页面引导分开，底层入口参数仍保持统一存储</p>
        </div>
        <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs text-indigo-700">重点区域</span>
      </div>

      <div class="mt-4 grid gap-3 lg:grid-cols-2">
        <div
          v-for="guide in clientGuides"
          :key="guide.id"
          class="rounded-2xl border p-4 text-left transition-all duration-150"
          :class="
            clientProfile === guide.id
              ? 'border-indigo-300 bg-indigo-50/80 shadow-[0_10px_30px_-20px_rgba(79,70,229,0.45)]'
              : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-slate-50'
          "
          @click="selectClientProfile(guide.id)"
        >
          <div class="flex items-center justify-between gap-3">
            <div>
              <p class="text-base font-medium text-slate-900">{{ guide.title }}</p>
              <p class="mt-1 text-sm text-slate-600">{{ guide.description }}</p>
            </div>
            <span
              class="rounded-full px-2.5 py-1 text-[11px]"
              :class="
                clientProfile === guide.id
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-600'
              "
            >
              {{ clientProfile === guide.id ? "当前选择" : guide.badge }}
            </span>
          </div>

          <div
            class="mt-4 grid gap-3 rounded-xl border border-slate-200/80 bg-white/80 p-3 sm:grid-cols-2"
          >
            <div>
              <p class="text-[11px] uppercase tracking-wide text-slate-400">推荐入口模型名</p>
              <p class="mt-1 break-all text-sm text-slate-800">{{ guide.modelPreview }}</p>
            </div>
            <div>
              <p class="text-[11px] uppercase tracking-wide text-slate-400">命名策略</p>
              <p class="mt-1 text-sm text-slate-700">{{ guide.namingHint }}</p>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between gap-3">
            <span class="text-xs text-slate-500">一键复制这套客户端填写说明</span>
            <div class="flex items-center gap-2">
              <span
                class="inline-flex items-center rounded-full px-2 py-1 text-[11px]"
                :class="
                  copiedGuideId === guide.id
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-slate-100 text-slate-500'
                "
              >
                {{ copiedGuideId === guide.id ? "已复制" : "可复制" }}
              </span>
              <button
                class="btn btn-xs rounded-lg border-0 bg-slate-900 text-white hover:bg-slate-800"
                @click.stop="copyClientGuide(guide.id)"
              >
                复制配置
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
      <div class="flex items-center justify-between gap-3 mb-3">
        <div>
          <p class="text-sm font-medium text-slate-900">当前运行摘要</p>
          <p class="mt-1 text-xs text-slate-600">
            这里显示当前真正生效的上游配置，便于避免多协议误读
          </p>
        </div>
        <button
          class="btn btn-xs btn-outline rounded-lg border-slate-200 px-3 text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700"
          @click="jumpToConfigGroup"
        >
          去配置组查看
        </button>
      </div>
      <div class="grid gap-3 sm:grid-cols-3">
        <div class="rounded-xl bg-slate-50 px-4 py-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">当前生效配置组</p>
          <p class="mt-1 text-sm text-slate-900">{{ activeGroupSummary.groupName }}</p>
        </div>
        <div class="rounded-xl bg-slate-50 px-4 py-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">当前上游协议</p>
          <p class="mt-1 text-sm text-slate-900">{{ activeGroupSummary.protocolLabel }}</p>
        </div>
        <div class="rounded-xl bg-slate-50 px-4 py-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">当前上游模型ID</p>
          <p class="mt-1 break-all text-sm text-slate-900">
            {{ activeGroupSummary.targetModelId }}
          </p>
        </div>
      </div>
      <p class="mt-3 text-xs text-slate-600">
        多协议共存时，请在“代理配置组”切换当前生效协议；本页两项始终只作为统一客户端入口。
      </p>
    </div>

    <div
      v-if="protocolMixNotice.show"
      class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 shadow-sm"
    >
      检测到同时存在 OpenAI 与 Anthropic Messages 配置组。当前仅配置组
      <span class="font-medium">{{ protocolMixNotice.activeGroupName }}</span>
      生效（{{ protocolMixNotice.activeProtocolLabel }}）。
    </div>

    <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-sm font-medium text-slate-900">统一入口参数</p>
          <p class="mt-1 text-xs text-slate-600">
            保存后会同步到所有配置组，但不会覆盖上游 API 参数
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button
            class="btn btn-xs btn-outline rounded-lg border-slate-200 px-3 text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700"
            @click="copyFieldValue('model')"
          >
            复制模型名
          </button>
          <button
            class="btn btn-xs btn-outline rounded-lg border-slate-200 px-3 text-slate-600 hover:border-indigo-400 hover:bg-indigo-50 hover:text-indigo-700"
            @click="copyFieldValue('key')"
          >
            复制访问Key
          </button>
        </div>
      </div>

      <div class="mt-4 space-y-4">
        <MtgaInput
          v-model="mappedModelId"
          label="客户端映射模型ID"
          :placeholder="selectedClientGuide.modelPreview"
          :description="mappedModelDescription"
          required
        />

        <div
          v-if="modelNameCollisionNotice.show"
          class="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800"
        >
          当前入口模型名
          <span class="font-medium">{{ modelNameCollisionNotice.matchedModelId }}</span>
          在 {{ selectedClientGuide.title }} 场景下容易与内置模型冲突。点击保存后将自动调整为
          <span class="font-medium">{{ modelNameCollisionNotice.suggestion }}</span
          >。
        </div>

        <MtgaInput
          v-model="mtgaAuthKey"
          label="客户端访问Key"
          placeholder="例如：client-access-key"
          :description="mtgaAuthDescription"
          type="password"
          required
        />
      </div>

      <div class="mt-5 flex items-center justify-between gap-3">
        <span class="text-xs text-slate-500">建议先确认当前配置组，再保存入口参数。</span>
        <button
          class="btn btn-primary btn-sm rounded-xl px-4"
          :disabled="saving"
          @click="handleSave"
        >
          保存全局配置
        </button>
      </div>
    </div>
  </div>
</template>
