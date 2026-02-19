# 启动诊断备忘

## 适用场景

- 启动偶发白屏、splash 卡住、后端连接瞬断。
- 打包环境下难以通过控制台定位问题。

## 关键经验

- `get_py_invoke_handler()` **可能被并发调用**，会导致 portal/handler 重复初始化并触发后端连接异常。
- 修复方式：在 `get_py_invoke_handler()` 内加互斥锁，确保只初始化一次。

## 诊断思路（按优先级）

1. **优先排查并发初始化**
   - 现象：日志中 `portal_context enter` 重复出现。
   - 处理：为 `get_py_invoke_handler()` 加锁并复测。
2. **只在需要时启用“深度诊断”**
   - 使用临时日志与故障捕获，定位 Python/运行时崩溃点。
   - **排查结束后务必移除**，避免污染生产环境。

## 临时诊断的注意事项

- `panic = "unwind"` 仅用于诊断 Rust panic；发布前应恢复为 `abort`。
- 若启用 `tauri-plugin-log` 与 `log:default` 能力，排查结束后应撤回权限。
- 如果使用 Python 侧的 `faulthandler` / 额外日志文件，排查完成后应移除。

## 诊断产物位置（历史记录）

- `%APPDATA%\MTGA\mtga_tauri_boot.log`：Python 启动阶段日志（临时诊断）。
- `%APPDATA%\MTGA\mtga_tauri_fault.log`：`faulthandler` 输出（临时诊断）。
- `%APPDATA%\MTGA\mtga_tauri_invoke.log`：Python invoke 路径日志（临时诊断）。
