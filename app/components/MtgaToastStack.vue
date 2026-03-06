<script setup lang="ts">
const { items, removeToast } = useMtgaToast();

const toneClassMap = {
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
  info: "border-sky-200 bg-sky-50 text-sky-700",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  error: "border-rose-200 bg-rose-50 text-rose-700",
} as const;
</script>

<template>
  <div
    class="pointer-events-none fixed right-5 top-5 z-[10000] flex w-[320px] max-w-[calc(100vw-2rem)] flex-col gap-2"
  >
    <TransitionGroup
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="translate-y-1 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-1 opacity-0"
    >
      <div
        v-for="item in items"
        :key="item.id"
        class="pointer-events-auto rounded-xl border px-3 py-2 text-sm shadow-lg"
        :class="toneClassMap[item.tone]"
      >
        <div class="flex items-start justify-between gap-3">
          <span class="leading-6">{{ item.message }}</span>
          <button
            class="btn btn-ghost btn-xs min-h-0 h-6 px-1 text-current opacity-70 hover:opacity-100"
            @click="removeToast(item.id)"
          >
            ×
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>
