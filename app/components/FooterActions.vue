<script setup lang="ts">
const store = useMtgaStore();

const handleStartAll = () => {
  store.runProxyStartAll();
};
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <div class="text-sm font-semibold text-slate-900">快速操作</div>
      <div class="text-xs text-slate-500">一键启动会依次检查网络、证书与 hosts 配置</div>
    </div>
    <button
      class="btn btn-primary px-8 rounded-xl shadow-[0_14px_30px_-12px_rgba(79,70,229,0.6)]"
      @click="handleStartAll"
    >
      一键启动全部服务
    </button>
  </div>
</template>
