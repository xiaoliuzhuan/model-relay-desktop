import type { AppInfo, ConfigPayload, MainTabKey, ProviderProtocol } from "./mtgaTypes";

export type SnapshotPanel =
  | "config-group"
  | "global-config"
  | "main-tabs"
  | "run-logs"
  | "settings";

export type SnapshotContext = {
  enabled: boolean;
  panel: SnapshotPanel;
  mainTab: MainTabKey;
  showUpdateDialog: boolean;
};

const DISABLED_FLAG_VALUES = new Set(["0", "false", "off", "no"]);
const UPDATE_DIALOG_ALIASES = new Set(["update", "dialog"]);
const SNAPSHOT_PANELS: SnapshotPanel[] = [
  "config-group",
  "global-config",
  "main-tabs",
  "run-logs",
  "settings",
];
const SNAPSHOT_MAIN_TABS: MainTabKey[] = ["cert", "hosts", "proxy"];

const coerceQueryValue = (value: unknown) => {
  if (Array.isArray(value)) {
    return coerceQueryValue(value[0]);
  }
  return typeof value === "string" ? value.trim() : "";
};

const isFlagEnabled = (value: string) => {
  if (!value) {
    return true;
  }
  return !DISABLED_FLAG_VALUES.has(value.toLowerCase());
};

const isOptionalEnvFlagEnabled = (value: string) => {
  if (!value) {
    return false;
  }
  return isFlagEnabled(value);
};

const normalizePanel = (value: string): SnapshotPanel | null => {
  if (!value) {
    return null;
  }
  return SNAPSHOT_PANELS.find((item) => item === value) ?? null;
};

const normalizeMainTab = (value: string): MainTabKey | null => {
  if (!value) {
    return null;
  }
  return SNAPSHOT_MAIN_TABS.find((item) => item === value) ?? null;
};

const cloneConfigGroup = (group: ConfigPayload["config_groups"][number]) => ({
  ...group,
});

const SNAPSHOT_CONFIG_PAYLOAD: ConfigPayload = {
  config_groups: [
    {
      name: "OpenAI 主线路",
      api_url: "https://api.openai.com",
      model_id: "gpt-4.1",
      api_key: "sk-live-openai-demo-0001",
      protocol: "openai",
      middle_route: "/v1",
      target_model_id: "gpt-4.1",
    },
    {
      name: "Anthropic 备用线路",
      api_url: "https://api.anthropic.com",
      model_id: "claude-3-7-sonnet-20250219",
      api_key: "sk-ant-demo-0002",
      protocol: "anthropic_messages",
      anthropic_version: "2023-06-01",
      middle_route: "/v1/messages",
      target_model_id: "claude-3-7-sonnet-20250219",
    },
  ],
  current_config_index: 1,
  mapped_model_id: "assistant-relay",
  mtga_auth_key: "relay-demo-key",
};

const SNAPSHOT_APP_INFO: AppInfo = {
  display_name: "Model Relay Desktop",
  version: "v3.1.0-snapshot",
  github_repo: "xiaoliuzhuan/model-relay-desktop",
  ca_common_name: "MODEL_RELAY_DESKTOP_CA",
  api_key_visible_chars: 4,
  user_data_dir: "/Users/demo/Library/Application Support/ModelRelayDesktop",
  default_user_data_dir: "/Users/demo/Library/Application Support/ModelRelayDesktop",
};

const SNAPSHOT_LOGS = [
  "🖼️ 快照模式已启用：当前界面使用内置演示数据渲染",
  "✅ 环境预检通过：可直接用于 UI 视觉回归检查",
  "✅ 已加载 2 个代理配置组（OpenAI / Anthropic）",
  "ℹ️ 当前生效配置组：Anthropic 备用线路",
  "ℹ️ 主要流程页支持 cert / hosts / proxy 三个步骤快照",
  "🔎 日志、设置与全局配置都来自确定性 mock 数据",
];

const SNAPSHOT_UPDATE = {
  versionLabel: "v3.2.0-beta.1",
  releaseUrl: "https://github.com/xiaoliuzhuan/model-relay-desktop/releases/tag/v3.2.0-beta.1",
  notesHtml: [
    "<ul>",
    "<li>统一刷新后的代理配置、主要流程与设置面板视觉语言。</li>",
    "<li>优化运行日志控制台的层级与可读性。</li>",
    "<li>新增轻量 Playwright 视觉快照校验流程。</li>",
    "</ul>",
    '<p>查看 <a href="/releases/tag/v3.2.0-beta.1">完整发布说明</a>。</p>',
  ].join(""),
};

const SNAPSHOT_MODEL_MAP: Record<ProviderProtocol, string[]> = {
  openai: ["gpt-4.1", "gpt-4.1-mini", "o3-mini"],
  anthropic_messages: ["claude-3-7-sonnet-20250219", "claude-3-5-haiku-20241022"],
};

export const useMtgaSnapshot = () => {
  const route = useRoute();
  const runtimeConfig = useRuntimeConfig();

  return computed<SnapshotContext>(() => {
    const hasSnapshotQuery = Object.prototype.hasOwnProperty.call(route.query, "snapshot");
    const snapshotFlag = coerceQueryValue(route.query.snapshot);
    const envFlag =
      typeof runtimeConfig.public.mtgaSnapshot === "string"
        ? runtimeConfig.public.mtgaSnapshot.trim()
        : "";
    const enabled = hasSnapshotQuery
      ? isFlagEnabled(snapshotFlag)
      : isOptionalEnvFlagEnabled(envFlag);
    const dialogFlag = coerceQueryValue(route.query.dialog).toLowerCase();
    const updateFlag = coerceQueryValue(route.query.update);
    const snapshotMode = snapshotFlag.toLowerCase();

    return {
      enabled,
      panel: normalizePanel(coerceQueryValue(route.query.panel)) ?? "config-group",
      mainTab:
        normalizeMainTab(
          coerceQueryValue(route.query.mainTab) ||
            coerceQueryValue(route.query.tab) ||
            coerceQueryValue(route.query.step),
        ) ?? "cert",
      showUpdateDialog:
        enabled &&
        (UPDATE_DIALOG_ALIASES.has(snapshotMode) ||
          UPDATE_DIALOG_ALIASES.has(dialogFlag) ||
          (Object.prototype.hasOwnProperty.call(route.query, "update") &&
            isFlagEnabled(updateFlag))),
    };
  });
};

export const createSnapshotConfigPayload = (): ConfigPayload => ({
  ...SNAPSHOT_CONFIG_PAYLOAD,
  config_groups: SNAPSHOT_CONFIG_PAYLOAD.config_groups.map(cloneConfigGroup),
});

export const createSnapshotAppInfo = (): AppInfo => ({
  ...SNAPSHOT_APP_INFO,
});

export const createSnapshotLogs = () => [...SNAPSHOT_LOGS];

export const createSnapshotUpdate = () => ({
  ...SNAPSHOT_UPDATE,
});

export const createSnapshotModels = (protocol?: ProviderProtocol | null) => [
  ...(SNAPSHOT_MODEL_MAP[protocol === "anthropic_messages" ? "anthropic_messages" : "openai"] ??
    SNAPSHOT_MODEL_MAP.openai),
];
