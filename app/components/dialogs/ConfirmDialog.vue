<script setup lang="ts">
/**
 * 基础确认对话框
 */
const props = withDefaults(
  defineProps<{
    open?: boolean
    title?: string
    message?: string
    confirmText?: string
    cancelText?: string
  }>(),
  {
    open: false,
    title: "确认操作",
    message: "请确认是否继续该操作。",
    confirmText: "确认",
    cancelText: "取消",
  }
)

const emit = defineEmits<{
  (event: "confirm"): void
  (event: "cancel"): void
  (event: "update:open", value: boolean): void
}>()

const openModel = computed({
  get: () => props.open,
  set: (value: boolean) => emit("update:open", value),
})

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
      <div>
        <h3 class="text-lg font-semibold text-slate-900">{{ props.title }}</h3>
      </div>
    </template>

    <div class="px-6 py-5">
      <div class="text-sm text-slate-600 leading-relaxed">
        <slot>{{ props.message }}</slot>
      </div>
    </div>

    <template #footer>
      <button class="mtga-btn-dialog-ghost flex-1" @click="handleCancel">
        {{ props.cancelText }}
      </button>
      <button class="mtga-btn-dialog-primary flex-1" @click="handleConfirm">
        {{ props.confirmText }}
      </button>
    </template>
  </MtgaDialog>
</template>
