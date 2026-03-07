<script setup lang="ts">
const store = useMtgaStore();

const handleModify = () => {
  store.runHostsModify("add");
};

const handleBackup = () => {
  store.runHostsModify("backup");
};

const handleRestore = () => {
  store.runHostsModify("restore");
};

const handleOpen = () => {
  store.runHostsOpen();
};
</script>

<template>
  <div class="space-y-4">
    <div class="mtga-panel-card">
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="text-sm font-medium text-slate-900">hosts 文件</div>
          <div class="mt-1 text-xs text-slate-600">系统级导流入口，适合先备份再修改</div>
        </div>
        <span class="mtga-status-pill">步骤 2</span>
      </div>

      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div class="mtga-panel-tile">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">主操作</p>
          <p class="mt-1 text-sm text-slate-900">写入或更新代理所需的 hosts 映射</p>
        </div>
        <div class="mtga-panel-tile">
          <p class="text-[11px] uppercase tracking-wide text-slate-400">维护建议</p>
          <p class="mt-1 text-sm text-slate-900">修改前先备份，必要时可直接打开文件核对内容</p>
        </div>
      </div>
    </div>

    <div class="grid gap-4 lg:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
      <div class="mtga-panel-card">
        <div>
          <div class="text-sm font-medium text-slate-900">主操作</div>
          <div class="mt-1 text-xs text-slate-600">按当前应用需求快速完成 hosts 导流修改</div>
        </div>
        <button class="mtga-btn-primary mt-4" @click="handleModify">修改 hosts 文件</button>
        <div
          class="mt-4 rounded-xl border border-indigo-100 bg-indigo-50 px-3 py-2 text-xs text-slate-700"
        >
          完成后建议切到代理页做网络检查，确认导流结果与证书状态一致。
        </div>
      </div>

      <div class="mtga-panel-card">
        <div>
          <div class="text-sm font-medium text-slate-900">维护与查看</div>
          <div class="mt-1 text-xs text-slate-600">备份、恢复和直接打开文件入口集中在这里</div>
        </div>
        <div class="mt-4 grid gap-2 sm:grid-cols-2">
          <button class="mtga-btn-outline" @click="handleBackup">备份 hosts</button>
          <button class="mtga-btn-outline" @click="handleRestore">还原 hosts</button>
          <button class="mtga-btn-outline sm:col-span-2" @click="handleOpen">
            打开 hosts 文件
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
