<script setup lang="ts">
const store = useMtgaStore()
const appInfo = store.appInfo

const isConfirmOpen = ref(false)
const inputCommonName = ref("")
const showInputError = ref(false)

const clearCaTooltip = computed(() => {
  const commonName = appInfo.value.ca_common_name || "MTGA_CA"
  return [
    "macOS: 删除系统钥匙串中匹配的CA证书；",
    "Windows: 删除本地计算机/Root 中匹配的CA证书",
    `Common Name: ${commonName}`,
    "需要管理员权限，建议仅在需要重置证书时使用",
  ].join("\n")
})

const handleGenerate = () => {
  store.runGenerateCertificates()
}

const handleInstall = () => {
  store.runInstallCaCert()
}

/**
 * 触发清除系统 CA 证书流程，先打开确认弹窗
 */
const handleClear = () => {
  inputCommonName.value = appInfo.value.ca_common_name || "MTGA_CA"
  showInputError.value = false
  isConfirmOpen.value = true
}

/**
 * 用户确认后的实际清除操作
 */
const confirmClear = () => {
  if (!inputCommonName.value.trim()) {
    showInputError.value = true
    return
  }
  isConfirmOpen.value = false
  store.runClearCaCert(inputCommonName.value)
}

watch(inputCommonName, (val) => {
  if (val.trim()) {
    showInputError.value = false
  }
})
</script>

<template>
  <div class="mtga-soft-panel space-y-3">
    <div>
      <div class="text-sm font-semibold text-slate-900">证书管理</div>
      <div class="text-xs text-slate-500">生成、安装与清理本地证书</div>
    </div>
    <div class="space-y-2">
      <button class="mtga-btn-primary" @click="handleGenerate">
        生成CA和服务器证书
      </button>
      <div class="grid grid-cols-2 gap-2">
        <button class="mtga-btn-primary" @click="handleInstall">安装CA证书</button>
        <button
          class="mtga-btn-error tooltip mtga-tooltip"
          :data-tip="clearCaTooltip"
          style="--mtga-tooltip-max: 280px;"
          @click="handleClear"
        >
          清除系统CA证书
        </button>
      </div>
    </div>
  </div>

  <!-- 二次确认弹窗 -->
  <dialog class="modal" :class="{ 'modal-open': isConfirmOpen }">
    <div class="modal-box mtga-card p-0 overflow-hidden max-w-sm border-slate-200/60 shadow-2xl">
      <div class="mtga-card-body p-6 space-y-4">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-full bg-error/10 text-error">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-slate-900">确认清除 CA 证书</h3>
        </div>
        
        <div class="flex flex-col gap-2">
          <p class="text-sm text-slate-600 leading-relaxed">
            将从系统信任存储中删除匹配的 CA 证书，是否继续？
          </p>

          <MtgaInput
            v-model="inputCommonName"
            label="Common Name:"
            placeholder="请输入证书 Common Name"
            :error="showInputError ? '请输入有效的 Common Name' : ''"
            input-class="font-mono"
          />
        </div>
      </div>

      <div class="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex items-center gap-3">
        <button class="btn btn-ghost btn-sm h-10 px-4 rounded-xl text-slate-500 flex-1" @click="isConfirmOpen = false">
          取消
        </button>
        <button 
          class="btn btn-error btn-sm h-10 px-6 rounded-xl text-white font-bold flex-[1.5] shadow-lg shadow-error/20" 
          @click="confirmClear"
        >
          确认清除
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop bg-slate-900/20 backdrop-blur-[2px]" @click="isConfirmOpen = false">
      <button>close</button>
    </form>
  </dialog>
</template>
