# 启动白屏排查记录与方案（更新版）

## 背景

- 项目：Model Relay Desktop（Tauri + Nuxt SPA）。
- 目标：解决“启动白屏”和“过渡页不稳定/不出现”，并稳定后端连接。

## 现状（已实现方案）

- **原生 Splash 窗口**：`public/splashscreen.html`（spinner + 文案），由 `src-tauri/tauri.conf.json` 配置为 `splash` 窗口。
- **主窗口**：`visible: false`（避免白屏闪现），等待后端 warmup + 主页面 ready 后再显示。
- **前端过渡页**：不再依赖 `#__nuxt-loader`（`app/spa-loading-template.html` 已清理）。
- **后端 warmup**：保留在后台线程执行，并由 splash 覆盖等待期。

## 关键发现（更新）

### 1) 白屏主要发生在 WebView 开始加载之前

- 在 `page_load Started` 之前存在明显空档，前端无法覆盖。
- 结论：**必须使用原生 Splash** 才能覆盖最早期空白。

### 2) Nuxt loader 容器不可靠

- `#__nuxt-loader` 会在 Nuxt 初始化阶段被清理，基于它的 overlay 会“看不到”或闪一下。
- 结论：**不能将过渡页托管在 `#__nuxt-loader`**。

### 3) 后端连接不稳的根因（已修复）

- 现象：日志出现 **`portal_context enter` 重复**，且“刚连接上就立刻断开”。
- 结论：`get_py_invoke_handler()` 被并发调用，导致 portal / handler 初始化重复。
- 修复：`python-src/mtga_app/__init__.py` 内 **增加互斥锁**，保证只初始化一次。
- 验证结果：加锁后连接稳定，重复 `portal_context enter` 不再出现。

## 日志与诊断入口（当前有效）

- Rust 启动日志：`%LOCALAPPDATA%\com.mtga.tauri\rs_boot.log`
- Python 启动日志：`%APPDATA%\MTGA\mtga_tauri_boot.log`
- Python fault 日志：`%APPDATA%\MTGA\mtga_tauri_fault.log`（若为空，通常是硬崩未触发 faulthandler）

## 当前推荐方案（稳定版）

1. **原生 Splash 窗口 + 主窗口延迟显示**：
   - 覆盖 `boot_start → page_load` 的空白期。
   - 避免“白屏闪一下”。
2. **后端 warmup 后再显示主窗口**：
   - 保证主窗口显示时后端已可用。
3. **后端初始化加锁**：
   - 避免并发初始化导致的连接异常。

## 完整时序（打点标签顺序）

1. Rust 进程启动：`boot_start`（内部记录，后续日志使用同一基准）
2. Python 初始化：`python_init_start` → `python_init_done`
3. Python handler 构建：`python_handler_ready`
4. Tauri 构建完成：`builder_done` → `app_built`
5. 事件循环准备：`run_ready`
6. 主窗口页面加载：`page_load Started (main)` → `page_load Finished (main)` → `main_page_ready`
7. Splash 页面加载：`page_load Started (splash)` → `page_load Finished (splash)` → `overlay_ready`
8. 后端 warmup：`backend_init_start` → `backend_warmup_begin` → `backend_warmup_done` → `backend_init_done`
9. 显示主窗口：`main_shown`（条件：`BACKEND_READY && MAIN_PAGE_READY`）
10. 关闭 splash：`splash_closed`
11. 前端挂载：`plugin_loaded` → `app_mounted`（Nuxt）

备注：

- `overlay_ready` 来自 `splashscreen.html`，若未触发，会有 1200ms fallback 触发 `start_backend_init`。
- `main_shown` 仅在 `BACKEND_READY` 与 `MAIN_PAGE_READY` 同时满足时触发；若任意一方晚到，则等待对方。

## 仍可选的优化方向

- 若需要进一步缩短启动时长：评估拆分/延迟 Python 初始化（风险需评估）。
- 若需更完整的早期诊断：在 Rust 侧增加 panic hook 或更多 native 级别日志。

## 关键代码位置（便于回溯）

- Splash 页面：`public/splashscreen.html`
  - 负责最早期可见反馈，加载后发送 `mtga:overlay-ready` 事件。
- 窗口配置：`src-tauri/tauri.conf.json`
  - `app.windows` 中定义 `main`（`visible: false`）与 `splash`。
- 启动/窗口时序：`src-tauri/src/lib.rs`
  - `start_backend_init`：后端 warmup 启动入口（后台线程）。
  - `run_backend_warmup`：warmup 打点与完成信号。
  - `try_show_main`：满足条件后显示主窗口并关闭 splash。
  - `on_page_load`：记录主页面 ready（用于触发显示条件）。
- 后端初始化锁：`python-src/mtga_app/__init__.py`
  - `get_py_invoke_handler`：入口加互斥锁，避免并发初始化导致断连。
