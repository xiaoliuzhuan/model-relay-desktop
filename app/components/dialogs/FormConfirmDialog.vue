<script setup lang="ts">
/**
 * 通用的带输入框的二次确认对话框组件
 */

const props = withDefaults(
  defineProps<{
    /** 是否显示对话框 */
    open?: boolean
    /** 对话框标题 */
    title?: string
    /** 提示消息 */
    message?: string
    /** 输入框绑定的值 */
    modelValue?: string
    /** 输入框标签 */
    label?: string
    /** 输入框占位符 */
    placeholder?: string
    /** 输入框错误提示 */
    error?: string
    /** 确认按钮文字 */
    confirmText?: string
    /** 取消按钮文字 */
    cancelText?: string
    /** 主题类型：primary 或 error */
    type?: 'primary' | 'error'
  }>(),
  {
    open: false,
    title: "确认操作",
    message: "",
    modelValue: "",
    label: "",
    placeholder: "",
    error: "",
    confirmText: "确认",
    cancelText: "取消",
    type: "primary",
  }
)

const emit = defineEmits<{
  (event: "update:open", value: boolean): void
  (event: "update:modelValue", value: string): void
  (event: "confirm"): void
  (event: "cancel"): void
}>()

const openModel = computed({
  get: () => props.open,
  set: (value: boolean) => emit("update:open", value),
})

const inputModel = computed({
  get: () => props.modelValue,
  set: (value: string) => emit("update:modelValue", value),
})

/**
 * 处理取消操作
 */
const handleCancel = () => {
  openModel.value = false
  emit("cancel")
}

const handleDialogClose = () => {
  emit("cancel")
}

/**
 * 处理确认操作
 */
const handleConfirm = () => {
  emit("confirm")
}
</script>

<template>
  <MtgaDialog v-model:open="openModel" max-width="max-w-sm" @close="handleDialogClose">
    <template #header>
      <div class="flex items-center gap-3">
        <div
          class="p-2 rounded-full"
          :class="props.type === 'error' ? 'bg-error/10 text-error' : 'bg-primary/10 text-primary'"
        >
          <slot name="icon">
            <!-- 默认图标 -->
            <svg v-if="props.type === 'error'" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </slot>
        </div>
        <h3 class="text-lg font-semibold text-slate-900 leading-none">{{ props.title }}</h3>
      </div>
    </template>

    <div class="px-6 py-5 space-y-3">
      <p v-if="props.message" class="text-sm text-slate-600 leading-relaxed">
        {{ props.message }}
      </p>

      <MtgaInput
        v-model="inputModel"
        :label="props.label"
        :placeholder="props.placeholder"
        :error="props.error"
        input-class="font-mono"
      />
    </div>

    <template #footer>
      <button class="btn btn-ghost btn-sm h-10 px-4 rounded-xl text-slate-500 flex-1" @click="handleCancel">
        {{ props.cancelText }}
      </button>
      <button
        class="btn btn-sm h-10 px-6 rounded-xl text-white font-bold flex-1 shadow-lg"
        :class="props.type === 'error' ? 'btn-error shadow-error/20' : 'btn-primary shadow-primary/20'"
        @click="handleConfirm"
      >
        {{ props.confirmText }}
      </button>
    </template>
  </MtgaDialog>
</template>
