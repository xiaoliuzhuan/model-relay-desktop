<script setup lang="ts">
const store = useMtgaStore();
const options = store.runtimeOptions;
const streamModeSummary = computed(() => {
  if (!options.value.forceStream) {
    return "跟随后端响应";
  }
  return options.value.streamMode === "false" ? "强制关闭" : "强制开启";
});

const debugModeTooltip = [
  "开启后：",
  "1) 代理服务器输出更详细的调试日志，便于排查问题；",
  "2) 启动代理服务器前会额外检查系统/环境变量的显式代理配置",
  "并提示其可能绕过 hosts 导流。",
  "（默认不做第 2 项检查，仅在调试模式下启用）",
].join("\n");

const handleStart = () => {
  store.runProxyStart();
};

const handleStop = () => {
  store.runProxyStop();
};

const handleCheck = () => {
  store.runProxyCheckNetwork();
};
</script>

<template>
  <div class="space-y-4">
    <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="text-sm font-medium text-slate-900">代理运行摘要</div>
          <div class="mt-1 text-xs text-slate-600">先确认运行时选项，再启动服务并检查网络环境</div>
        </div>
        <span class="rounded-full bg-indigo-50 px-3 py-1 text-xs text-indigo-700">步骤 3</span>
      </div>

      <div class="mt-4 grid gap-3 sm:grid-cols-3">
        <div class="rounded-xl bg-slate-50 px-4 py-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">调试模式</p>
          <p class="mt-1 text-sm text-slate-900">{{ options.debugMode ? "开启" : "关闭" }}</p>
        </div>
        <div class="rounded-xl bg-slate-50 px-4 py-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">SSL 严格模式</p>
          <p class="mt-1 text-sm text-slate-900">
            {{ options.disableSslStrict ? "已关闭" : "保持开启" }}
          </p>
        </div>
        <div class="rounded-xl bg-slate-50 px-4 py-3">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">流式输出</p>
          <p class="mt-1 text-sm text-slate-900">{{ streamModeSummary }}</p>
        </div>
      </div>
    </div>

    <div class="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(300px,0.9fr)]">
      <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
        <div>
          <div class="text-sm font-medium text-slate-900">运行时选项</div>
          <div class="mt-1 text-xs text-slate-600">控制代理运行行为、日志粒度与流式输出策略</div>
        </div>

        <div class="mt-4 grid gap-3">
          <label
            class="rounded-xl border border-slate-200/80 bg-slate-50/80 px-4 py-3 transition-all hover:border-indigo-200 hover:bg-white tooltip mtga-tooltip cursor-pointer"
            :data-tip="debugModeTooltip"
            style="--mtga-tooltip-max: 500px"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="text-sm font-medium text-slate-900">调试模式</div>
                <div class="mt-1 text-xs text-slate-600">
                  输出更详细日志，并额外检查显式代理配置是否可能绕过 hosts。
                </div>
              </div>
              <input
                v-model="options.debugMode"
                type="checkbox"
                class="checkbox checkbox-sm mt-0.5 shrink-0"
              />
            </div>
          </label>

          <label
            class="rounded-xl border border-slate-200/80 bg-slate-50/80 px-4 py-3 transition-all hover:border-indigo-200 hover:bg-white cursor-pointer"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="text-sm font-medium text-slate-900">SSL 严格模式</div>
                <div class="mt-1 text-xs text-slate-600">
                  遇到特殊代理或测试环境时，可临时关闭严格校验辅助排查。
                </div>
              </div>
              <input
                v-model="options.disableSslStrict"
                type="checkbox"
                class="checkbox checkbox-sm mt-0.5 shrink-0"
              />
            </div>
          </label>

          <div class="rounded-xl border border-slate-200/80 bg-slate-50/80 px-4 py-3">
            <div class="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div class="text-sm font-medium text-slate-900">强制流模式</div>
                <div class="mt-1 text-xs text-slate-600">
                  固定代理输出的流式行为，未开启时默认跟随后端真实响应。
                </div>
              </div>
              <label class="flex items-center gap-3 cursor-pointer text-sm text-slate-700">
                <input v-model="options.forceStream" type="checkbox" class="checkbox checkbox-sm" />
                <span>启用</span>
              </label>
            </div>

            <div class="mt-3 flex flex-wrap items-center gap-2">
              <MtgaSelect
                v-model="options.streamMode"
                :options="['true', 'false']"
                size="xs"
                class="w-24"
                :disabled="!options.forceStream"
              />
              <span class="text-xs text-slate-500">
                {{ options.forceStream ? "已固定输出模式" : "关闭后按上游返回处理" }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200/80 bg-white/75 p-4 shadow-sm">
        <div>
          <div class="text-sm font-medium text-slate-900">代理服务</div>
          <div class="mt-1 text-xs text-slate-600">启动、停止与网络检查入口集中在同一张卡片里</div>
        </div>
        <div class="mt-4 space-y-2">
          <button class="mtga-btn-primary" @click="handleStart">启动代理服务器</button>
          <button class="mtga-btn-error" @click="handleStop">停止代理服务器</button>
          <button class="mtga-btn-outline" @click="handleCheck">检查网络环境</button>
        </div>
        <div
          class="mt-4 rounded-xl border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-slate-700"
        >
          启动前建议先完成证书与 hosts 两步，便于系统信任与域名导流一次到位。
        </div>
      </div>
    </div>
  </div>
</template>
