<script setup lang="ts">
withDefaults(
  defineProps<{
    rightHidden?: boolean;
  }>(),
  {
    rightHidden: false,
  },
);
</script>

<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <!-- 统一的容器：更清晰的层次与轻玻璃 -->
    <div
      class="flex-1 flex flex-col overflow-hidden border border-white/40 bg-white/55 shadow-[0_25px_60px_-35px_rgba(79,70,229,0.35)] backdrop-blur-md"
    >
      <!-- 顶部标题区域 -->
      <header class="w-full px-8 py-6 shrink-0 border-b border-indigo-100/70 bg-white/65">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-indigo-400">Console</p>
            <h1 class="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
              <slot name="title">MTGA</slot>
            </h1>
            <div class="mt-2 text-sm text-slate-600">
              <slot name="subtitle">一站式 AI 代理服务器管理面板</slot>
            </div>
          </div>
        </div>
      </header>

      <!-- 中间内容区域 -->
      <main class="flex-1 flex min-h-0">
        <section class="flex flex-col min-w-0" :class="rightHidden ? 'flex-1' : 'flex-7'">
          <slot name="left" />
        </section>

        <template v-if="!rightHidden">
          <div class="w-px bg-indigo-100/80 self-stretch shrink-0"></div>
          <section class="flex-5 flex flex-col min-w-0">
            <slot name="right" />
          </section>
        </template>
      </main>

      <!-- 底部操作区域 -->
      <footer class="p-5 shrink-0 border-t border-indigo-100/80 bg-white/70">
        <slot name="footer" />
      </footer>
    </div>
  </div>
</template>
