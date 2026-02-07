<script setup lang="ts">
/**
 * 通用确认对话框（支持可选输入框）
 */
const props = withDefaults(
  defineProps<{
    open?: boolean
    title?: string
    message?: string
    type?: "info" | "error"
    showInput?: boolean
    modelValue?: string
    label?: string
    placeholder?: string
    error?: string
    inputClass?: string
    confirmText?: string
    cancelText?: string
  }>(),
  {
    open: false,
    title: "确认操作",
    message: "请确认是否继续该操作。",
    type: "info",
    showInput: false,
    modelValue: "",
    label: "",
    placeholder: "",
    error: "",
    inputClass: "",
    confirmText: "确认",
    cancelText: "取消",
  }
)

const emit = defineEmits<{
  (event: "confirm"): void
  (event: "cancel"): void
  (event: "update:open", value: boolean): void
  (event: "update:modelValue", value: string): void
}>()

const openModel = computed({
  get: () => props.open,
  set: (value: boolean) => emit("update:open", value),
})

const inputModel = computed({
  get: () => props.modelValue,
  set: (value: string) => emit("update:modelValue", value),
})

const normalizedType = computed<"info" | "error">(() =>
  props.type === "error" ? "error" : "info"
)

const emitCancel = () => {
  emit("cancel")
}

const handleCancel = () => {
  openModel.value = false
  emitCancel()
}

const handleDialogClose = () => {
  emitCancel()
}

const handleConfirm = () => {
  emit("confirm")
}
</script>

<template>
  <MtgaDialog v-model:open="openModel" @close="handleDialogClose">
    <template #header>
      <div class="flex items-center gap-3">
        <div
          class="p-2 rounded-full"
          :class="normalizedType === 'error' ? 'bg-error/10 text-error' : 'bg-primary/10 text-primary'"
        >
          <slot name="icon">
            <svg v-if="normalizedType === 'error'" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8h.01M11 12h1v4h1m8-4a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </slot>
        </div>
        <h3 class="text-lg font-semibold text-slate-900 leading-none">{{ props.title }}</h3>
      </div>
    </template>

    <div class="px-6 py-5 space-y-3">
      <div class="text-sm text-slate-600 leading-relaxed">
        <slot>{{ props.message }}</slot>
      </div>

      <MtgaInput
        v-if="props.showInput"
        v-model="inputModel"
        :label="props.label"
        :placeholder="props.placeholder"
        :error="props.error"
        :input-class="props.inputClass"
      />
    </div>

    <template #footer>
      <button class="mtga-btn-dialog-ghost flex-1" @click="handleCancel">
        {{ props.cancelText }}
      </button>
      <button
        class="flex-1"
        :class="normalizedType === 'error' ? 'mtga-btn-dialog-error' : 'mtga-btn-dialog-primary'"
        @click="handleConfirm"
      >
        {{ props.confirmText }}
      </button>
    </template>
  </MtgaDialog>
</template>
