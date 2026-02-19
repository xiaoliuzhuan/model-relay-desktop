<template>
  <div class="h-screen flex flex-col overflow-hidden">
    <!-- 统一的毛玻璃容器，现在充满整个窗口 -->
    <div class="flex-1 flex flex-col bg-white/20 backdrop-blur-md overflow-hidden">
      <!-- 顶部标题区域 -->
      <header class="w-full px-8 py-6 shrink-0 border-b border-slate-200/60">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400">Console</p>
            <h1 class="mt-2 text-2xl font-semibold tracking-tight text-slate-900">
              <slot name="title">MTGA</slot>
            </h1>
            <div class="mt-2 text-sm text-slate-500">
              <slot name="subtitle">一站式 AI 代理服务器管理面板</slot>
            </div>
          </div>
        </div>
      </header>

      <!-- 中间内容区域 -->
      <main class="flex-1 flex min-h-0">
        <!-- 左侧区域 (占据 7/12) -->
        <section class="flex-7 flex flex-col min-w-0">
          <slot name="left" />
        </section>

        <!-- 垂直分割线 -->
        <div class="w-px bg-slate-200/60 self-stretch shrink-0"></div>

        <!-- 右侧区域 (占据 5/12) -->
        <section class="flex-5 flex flex-col min-w-0">
          <slot name="right" />
        </section>
      </main>

      <!-- 底部操作区域 -->
      <footer class="p-5 shrink-0 border-t border-slate-200/60">
        <slot name="footer" />
      </footer>
    </div>
  </div>
</template>
